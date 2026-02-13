import pytest


def test_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "Tennis Club" in data
    assert "Drama Club" in data
    
    # Verify activity structure
    activity = data["Basketball"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    response = client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    assert "Basketball" in data["message"]
    
    # Verify the student was added
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities["Basketball"]["participants"]


def test_signup_for_activity_not_found(client):
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonexistentActivity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_student(client):
    """Test that students cannot sign up twice for the same activity"""
    email = "duplicate@mergington.edu"
    
    # First signup should succeed
    response1 = client.post(f"/activities/Basketball/signup?email={email}")
    assert response1.status_code == 200
    
    # Second signup should fail
    response2 = client.post(f"/activities/Basketball/signup?email={email}")
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_remove_participant_success(client):
    """Test successfully removing a participant"""
    email = "to_remove@mergington.edu"
    
    # First, sign up the student
    client.post(f"/activities/Tennis%20Club/signup?email={email}")
    
    # Verify they're in the list
    activities = client.get("/activities").json()
    assert email in activities["Tennis Club"]["participants"]
    
    # Remove the participant
    response = client.delete(f"/activities/Tennis%20Club/participants/{email}")
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    
    # Verify they're no longer in the list
    activities = client.get("/activities").json()
    assert email not in activities["Tennis Club"]["participants"]


def test_remove_participant_not_found_activity(client):
    """Test removing participant from non-existent activity"""
    response = client.delete("/activities/NonexistentActivity/participants/test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_found_participant(client):
    """Test removing non-existent participant from activity"""
    response = client.delete("/activities/Basketball/participants/notregistered@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]
