# -*- coding: utf-8 -*-
import pytest

from utils import error, mgmt_system, testgen
from utils.randomness import generate_random_string
from utils.wait import wait_for

pytest_generate_tests = testgen.generate(
    testgen.provider_by_type,
    ['virtualcenter', 'rhevm'],
    "small_template",
    scope="module"
)

pytestmark = [pytest.mark.ignore_stream("5.2")]


@pytest.fixture(scope="module")
def provision_data(
        rest_api_modscope, provider_crud, provider_key, provider_data, small_template,
        provider_mgmt):
    templates = rest_api_modscope.collections.templates.find_by(name=small_template)
    for template in templates:
        if template.ems.name == provider_data["name"]:
            guid = template.guid
            break
    else:
        raise Exception("No such template {} on provider!".format(small_template))
    result = {
        "version": "1.1",
        "template_fields": {
            "guid": guid
        },
        "vm_fields": {
            "number_of_cpus": 1,
            "vm_name": "test_rest_prov_{}".format(generate_random_string()),
            "vm_memory": "2048",
            "vlan": provider_data["provisioning"]["vlan"],
        },
        "requester": {
            "user_name": "admin",
            "owner_first_name": "John",
            "owner_last_name": "Doe",
            "owner_email": "jdoe@sample.com",
            "auto_approve": True
        },
        "tags": {
            "network_location": "Internal",
            "cc": "001"
        },
        "additional_values": {
            "request_id": "1001"
        },
        "ems_custom_attributes": {},
        "miq_custom_attributes": {}
    }
    if isinstance(provider_mgmt, mgmt_system.RHEVMSystem):
        result["vm_fields"]["provision_type"] = "native_clone"
    return result


@pytest.mark.meta(server_roles="+automate")
@pytest.mark.usefixtures("setup_provider")
def test_provision(request, provision_data, provider_mgmt, rest_api):
    """Tests provision via rest

    Metadata:
        test_flag: rest, provision
    """

    vm_name = provision_data["vm_fields"]["vm_name"]
    request.addfinalizer(
        lambda: provider_mgmt.delete_vm(vm_name) if provider_mgmt.does_vm_exist(vm_name) else None)
    request = rest_api.collections.provision_requests.action.create(**provision_data)[0]

    def _finished():
        request.reload()
        if request.status.lower() in {"error"}:
            pytest.fail("Error when provisioning: `{}`".format(request.message))
        return request.request_state.lower() in {"finished", "provisioned"}

    wait_for(_finished, num_sec=600, delay=5, message="REST provisioning finishes")
    assert provider_mgmt.does_vm_exist(vm_name), "The VM {} does not exist!".format(vm_name)


def test_add_delete_service_catalog(rest_api):
    scl = rest_api.collections.service_catalogs.action.add(
        name=generate_random_string(),
        description=generate_random_string(),
        service_templates=[]
    )[0]
    scl.action.delete()
    with error.expected("ActiveRecord::RecordNotFound"):
        scl.action.delete()


def test_add_delete_multiple_service_catalogs(rest_api):
    def _gen_ctl():
        return {
            "name": generate_random_string(),
            "description": generate_random_string(),
            "service_templates": []
        }
    scls = rest_api.collections.service_catalogs.action.add(
        *[_gen_ctl() for _ in range(4)]
    )
    rest_api.collections.service_catalogs.action.delete(*scls)
    with error.expected("ActiveRecord::RecordNotFound"):
        rest_api.collections.service_catalogs.action.delete(*scls)
