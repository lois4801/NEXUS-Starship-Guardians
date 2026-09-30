from nexus_os.guardian_teams import artificial_architecture_team


def test_artificial_architecture_team_has_30_unique_guardians():
    team = artificial_architecture_team()
    assert len(team) == 30
    assert len({guardian.name for guardian in team}) == 30
    assert all("Guardian" in guardian.name for guardian in team)
