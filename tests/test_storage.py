"""Tests for DataStorage."""

import json
from pathlib import Path

import pytest

from shift_scheduling.factories import AgentFactory, AssignmentFactory, ShiftFactory
from shift_scheduling.storage import DataStorage


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def storage(sample_data_path: Path) -> DataStorage:
    storage = DataStorage(sample_data_path)
    storage.load()
    return storage


class TestLoadAndSave:
    def test_load_reads_every_list(self, storage: DataStorage):
        assert [a.id for a in storage.agents] == ["agt_1", "agt_2", "agt_3"]
        assert [s.id for s in storage.shifts] == ["shf_1", "shf_2"]
        assert [a.id for a in storage.assignments] == ["asg_1"]

    def test_save_round_trips_the_sample_data(
        self, storage: DataStorage, sample_data_path: Path
    ):
        before = read(sample_data_path)
        storage.save()
        assert read(sample_data_path) == before

    def test_save_leaves_no_temporary_files(
        self, storage: DataStorage, sample_data_path: Path
    ):
        storage.save()
        assert list(sample_data_path.parent.glob("*.tmp")) == []


class TestFinders:
    def test_find_agent(self, storage: DataStorage):
        assert storage.find_agent("agt_3").name == "Marc Tremblay"
        assert storage.find_agent("agt_missing") is None

    def test_assignments_for_shift(self, storage: DataStorage):
        assert [a.id for a in storage.assignments_for_shift("shf_1")] == ["asg_1"]
        assert storage.assignments_for_shift("shf_2") == []


class TestNextAssignmentId:
    def test_starts_at_one_when_empty(self, tmp_path: Path):
        assert DataStorage(tmp_path / "data.json").next_assignment_id() == "asg_1"

    def test_is_one_more_than_the_highest_number(self, tmp_path: Path):
        storage = DataStorage(tmp_path / "data.json")
        storage.assignments = [
            AssignmentFactory(id="asg_2"),
            AssignmentFactory(id="asg_10"),
        ]
        assert storage.next_assignment_id() == "asg_11"

    def test_ignores_ids_not_in_the_asg_number_format(self, tmp_path: Path):
        storage = DataStorage(tmp_path / "data.json")
        storage.assignments = [
            AssignmentFactory(id="asg_3"),
            AssignmentFactory(id="legacy-7"),
        ]
        assert storage.next_assignment_id() == "asg_4"


class TestAddAssignment:
    def test_persists_to_disk_and_memory(
        self, storage: DataStorage, sample_data_path: Path
    ):
        assignment = AssignmentFactory(id="asg_2", shift_id="shf_2", agent_id="agt_3")

        storage.add_assignment(assignment)

        assert storage.assignments[-1] == assignment
        assert read(sample_data_path)["assignments"][-1] == assignment.to_dict()

    def test_failed_write_leaves_memory_and_disk_unchanged(
        self,
        storage: DataStorage,
        sample_data_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        before_disk = read(sample_data_path)
        before_memory = list(storage.assignments)

        def failing_save():
            raise OSError("disk full")

        monkeypatch.setattr(storage, "save", failing_save)

        with pytest.raises(OSError):
            storage.add_assignment(AssignmentFactory())

        assert storage.assignments == before_memory
        assert read(sample_data_path) == before_disk

    def test_saved_file_can_be_loaded_again(self, tmp_path: Path):
        path = tmp_path / "data.json"
        storage = DataStorage(path)
        agent, shift = AgentFactory(), ShiftFactory()
        storage.agents, storage.shifts = [agent], [shift]

        storage.add_assignment(AssignmentFactory(agent_id=agent.id, shift_id=shift.id))

        reloaded = DataStorage(path)
        reloaded.load()
        assert reloaded.agents == [agent]
        assert reloaded.shifts == [shift]
        assert reloaded.assignments == storage.assignments
