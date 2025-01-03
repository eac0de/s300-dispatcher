from datetime import datetime, timedelta

import jsony
import pytest
from beanie import PydanticObjectId
from client.s300.models.employee import EmployeeS300
from client.s300.models.tenant import TenantS300
from file_manager import File
from httpx import AsyncClient
from models.appeal.appeal import Appeal
from models.appeal.constants import AppealStatus, AppealType
from models.appeal.embs.answer import AnswerAS, EmployeeAnswerAS
from models.appeal_category.appeal_category import AppealCategory
from models.appeal_comment.appeal_comment import AppealComment
from starlette import status


class TestDispatcherAppealRouter:

    @pytest.mark.usefixtures("departments")
    async def test_create_appeal(self, api_employee_client: AsyncClient, auth_tenant: TenantS300, appeal_categories: list, auth_employee: EmployeeS300):
        data = {
            "subject": "test_subject",
            "description": "test_description",
            "appealer": {"_id": auth_tenant.id},
            "_type": AppealType.ACKNOWLEDGEMENT,
            "observers": {"departments": [{"_id": auth_employee.department.id}]},
            "category_ids": set([appeal_categories[0].id]),
        }
        resp = await api_employee_client.post("/dispatcher/appeals/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_201_CREATED
        resp_json = resp.json()
        assert isinstance(resp_json, dict)

    async def test_get_appeal_stats(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        resp = await api_employee_client.get("/dispatcher/appeals/stats/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json == {"run": 1, "accepted": 1, "performed": 0, "overdue": 0}

        appeal = appeals[0]
        t = datetime.now() - timedelta(days=2)
        appeal.deadline_at = t
        await appeal.save()
        resp = await api_employee_client.get("/dispatcher/appeals/stats/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json == {"run": 1, "accepted": 1, "performed": 0, "overdue": 1}

    async def test_get_appeals_list(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        resp = await api_employee_client.get("/dispatcher/appeals/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("count") == 2
        assert resp_json.get("result") is not None

        resp = await api_employee_client.get("/dispatcher/appeals/", params={"status__in": appeal.status.value})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("count") == 1
        assert resp_json.get("result") is not None
        assert resp_json["result"][0]["_id"] == str(appeal.id)

        resp = await api_employee_client.get("/dispatcher/appeals/", params={"status__in": "test_no_status__in"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        resp = await api_employee_client.get("/dispatcher/appeals/", params={"number": appeal.number})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("count") == 1
        assert resp_json.get("result") is not None
        assert resp_json["result"][0]["_id"] == str(appeal.id)

    async def test_get_appeal(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json["_id"] == str(appeal.id)

    async def test_update_appeal(self, api_employee_client: AsyncClient, appeals: list[Appeal], appeal_categories: list[AppealCategory]):
        appeal = appeals[0]
        test_type = AppealType.CONSULTATION
        test_category_ids = set([appeal_categories[0].id])
        test_is_answer_required = True
        test_incoming_number = "123"
        test_incoming_at = datetime.now().replace(microsecond=0)
        data = {
            "_type": test_type,
            "category_ids": test_category_ids,
            "is_answer_required": test_is_answer_required,
            "incoming_number": test_incoming_number,
            "incoming_at": test_incoming_at,
        }
        resp = await api_employee_client.patch(f"/dispatcher/appeals/{appeal.id}/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal.sync()
        assert resp_json.get("_type") is not None
        assert appeal.type == test_type == resp_json["_type"]
        assert appeal.category_ids == test_category_ids == set(PydanticObjectId(cid) for cid in resp_json["category_ids"])
        assert appeal.is_answer_required == test_is_answer_required == resp_json["is_answer_required"]
        assert appeal.incoming_number == test_incoming_number == resp_json["incoming_number"]
        assert appeal.incoming_at == test_incoming_at == datetime.fromisoformat(resp_json["incoming_at"])

    async def test_accept_appeal(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300, appeals: list[Appeal]):
        appeal = appeals[0]
        resp = await api_employee_client.patch(f"/dispatcher/appeals/{appeal.id}/accept/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal.sync()
        assert appeal.executor is not None
        assert appeal.executor.id == auth_employee.id
        assert appeal.status == AppealStatus.RUN

    async def test_delete_appeal(self, api_employee_client: AsyncClient, appeals: list[Appeal]):

        appeal = appeals[0]
        resp = await api_employee_client.delete(f"/dispatcher/appeals/{appeal.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        a = await Appeal.get(appeal.id)
        assert a is None

    async def test_answer_appeal(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[1]
        text_answer_text = "test_answer"
        data = {"text": text_answer_text}
        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/answers/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal.sync()
        assert resp_json.get("answer") is not None
        assert appeal.answer is not None
        assert resp_json["answer"]["text"] == text_answer_text == appeal.answer.text
        assert resp_json["answer"]["is_published"] == False == appeal.answer.is_published
        assert resp_json.get("add_answers") is not None
        assert len(resp_json["add_answers"]) == 0 == len(appeal.add_answers)
        assert resp_json.get("status") is not None
        assert resp_json["status"] == AppealStatus.RUN == appeal.status

        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/answers/", json=data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

        resp = await api_employee_client.patch(f"/dispatcher/appeals/{appeal.id}/answers/{appeal.answer.id}/publish/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal.sync()
        assert resp_json.get("answer") is not None
        assert appeal.answer is not None
        assert resp_json["answer"]["text"] == text_answer_text == appeal.answer.text
        assert resp_json["answer"]["is_published"] == True == appeal.answer.is_published
        assert resp_json.get("add_answers") is not None
        assert len(resp_json["add_answers"]) == 0 == len(appeal.add_answers)
        assert resp_json.get("status") is not None
        assert resp_json["status"] == AppealStatus.PERFORMED == appeal.status

        text_add_answer_text = "test_add_answer"
        data = {"text": text_add_answer_text}
        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/answers/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal.sync()
        assert resp_json.get("add_answers") is not None
        assert len(appeal.add_answers) == 1 == len(resp_json["add_answers"])
        assert resp_json["add_answers"][0]["text"] == text_add_answer_text == appeal.add_answers[0].text
        assert resp_json["add_answers"][0]["is_published"] == False == appeal.add_answers[0].is_published
        assert resp_json.get("status") is not None
        assert resp_json["status"] == AppealStatus.PERFORMED == appeal.status

    async def test_upload_appealer_files(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/appealer_files/", files=files)
        assert resp.status_code == status.HTTP_200_OK
        await appeal.sync()
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files) == len(appeal.appealer_files)

    async def test_download_appealer_file(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"appeal appealer_files {appeal.id}")
        appeal.appealer_files.append(file)
        await appeal.save()
        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/appealer_files/{file.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert "text/plain" in resp.headers["Content-Type"]
        assert await resp.aread() == file_content

    async def test_upload_answer_files(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300, appeals: list[Appeal]):
        appeal = appeals[0]
        appeal.answer = AnswerAS(text="test_answer", employee=EmployeeAnswerAS.model_validate(auth_employee.model_dump(by_alias=True)))
        await appeal.save()
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/answers/{appeal.answer.id}/files/", files=files)
        assert resp.status_code == status.HTTP_200_OK
        await appeal.sync()
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("answer") is not None
        assert resp_json["answer"].get("files") is not None
        assert len(resp_json["answer"]["files"]) == len(files) == len(appeal.answer.files)

    async def test_download_answer_file(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300, appeals: list[Appeal]):
        appeal = appeals[0]
        appeal.answer = AnswerAS(text="test_answer", employee=EmployeeAnswerAS.model_validate(auth_employee.model_dump(by_alias=True)))
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"appeal answer {appeal.id}")
        appeal.answer.files.append(file)
        await appeal.save()
        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/answers/{appeal.answer.id}/files/{file.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert "text/plain" in resp.headers["Content-Type"]
        assert await resp.aread() == file_content

    async def test_update_appeal_answer(self, api_employee_client: AsyncClient, auth_employee: EmployeeS300, appeals: list[Appeal]):
        appeal = appeals[0]
        appeal.answer = AnswerAS(text="test_answer", employee=EmployeeAnswerAS.model_validate(auth_employee.model_dump(by_alias=True)))
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"appeal answer {appeal.id}")
        appeal.answer.files.append(file)
        await appeal.save()
        new_answer_text = "new_answer_text"
        data = {
            "text": new_answer_text,
            "files": [],
        }
        resp = await api_employee_client.patch(f"/dispatcher/appeals/{appeal.id}/answers/{appeal.answer.id}/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal.sync()
        assert resp_json.get("answer") is not None
        assert resp_json["answer"].get("text") is not None
        assert resp_json["answer"].get("files") is not None
        assert appeal.answer.text == new_answer_text == resp_json["answer"]["text"]
        assert len(resp_json["answer"]["files"]) == 0 == len(appeal.answer.files)

    @pytest.mark.usefixtures("appeal_comments")
    async def test_comment_appeal(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        text_comment_text = "test_comment_text"
        data = {"text": text_comment_text}
        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/comments/", json=data)
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("_id") is not None
        comment = await AppealComment.get(resp_json["_id"])
        assert comment is not None
        assert comment.text == text_comment_text
        assert comment.appeal_id == appeal.id

        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        assert resp_json.get("comment_stats") is not None
        assert resp_json["comment_stats"].get("all") is not None
        assert resp_json["comment_stats"]["all"] == 3

    @pytest.mark.usefixtures("appeal_comments")
    async def test_get_appeal_comments_list(self, api_employee_client: AsyncClient, appeals: list[Appeal]):
        appeal = appeals[0]
        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/comments/")
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 2

        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/comments/", params={"limit": 1})
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == 1

    async def test_update_appeal_comment(self, api_employee_client: AsyncClient, appeals: list[Appeal], appeal_comments: list[AppealComment]):
        appeal = appeals[0]
        appeal_comment = appeal_comments[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"appeal answer {appeal.id}")
        appeal_comment.files.append(file)
        await appeal_comment.save()
        new_appeal_comment_text = "new_comment_text"
        data = {
            "text": new_appeal_comment_text,
            "files": [],
        }
        resp = await api_employee_client.patch(f"/dispatcher/appeals/{appeal.id}/comments/{appeal_comment.id}/", json=jsony.normalize(data))
        assert resp.status_code == status.HTTP_200_OK
        resp_json = resp.json()
        assert isinstance(resp_json, dict)
        await appeal_comment.sync()
        assert resp_json.get("files") is not None
        assert resp_json.get("text") is not None
        assert appeal_comment.text == new_appeal_comment_text == resp_json["text"]
        assert len(resp_json["files"]) == 0 == len(appeal_comment.files)

    async def test_upload_comment_files(self, api_employee_client: AsyncClient, appeals: list[Appeal], appeal_comments: list[AppealComment]):
        appeal = appeals[0]
        appeal_comment = appeal_comments[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"appeal answer {appeal.id}")
        appeal_comment.files.append(file)
        await appeal_comment.save()
        files = [("files", ("file1.txt", b"file_content_1", "text/plain")), ("files", ("file2.txt", b"file_content_2", "text/plain"))]
        resp = await api_employee_client.post(f"/dispatcher/appeals/{appeal.id}/comments/{appeal_comment.id}/files/", files=files)
        assert resp.status_code == status.HTTP_200_OK
        await appeal_comment.sync()
        resp_json = resp.json()
        assert isinstance(resp_json, list)
        assert len(resp_json) == len(files) + 1 == len(appeal_comment.files)

    async def test_download_comment_file(self, api_employee_client: AsyncClient, appeals: list[Appeal], appeal_comments: list[AppealComment]):
        appeal = appeals[0]
        appeal_comment = appeal_comments[0]
        file_content = b"file_content_1"
        file = await File.create(file_content, "file1.txt", f"appeal answer {appeal.id}")
        appeal_comment.files.append(file)
        await appeal_comment.save()
        resp = await api_employee_client.get(f"/dispatcher/appeals/{appeal.id}/comments/{appeal_comment.id}/files/{appeal_comment.files[0].id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert "Content-Disposition" in resp.headers
        assert "text/plain" in resp.headers["Content-Type"]
        assert await resp.aread() == file_content
