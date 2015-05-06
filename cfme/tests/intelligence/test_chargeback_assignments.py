import pytest
import cfme.intelligence.chargeback as cb
import cfme.web_ui.flash as flash

pytestmark = [pytest.mark.usefixtures("logged_in")]


def test_assign_enterprise():

    enterprise = cb.Assign(
        assign_to="The Enterprise")
    enterprise.computeassign()

    flash.assert_message_match('Rate Assignments saved')


def test_assign_provider():

    provider = cb.Assign(
        assign_to="Selected Cloud/Infrastructure Providers")
    provider.computeassign()

    flash.assert_message_match('Rate Assignments saved')


def test_assign_cluster():

    enterprise = cb.Assign(
        assign_to="The Enterprise")
    enterprise.computeassign()

    flash.assert_message_match('Rate Assignments saved')


def test_assign_taggedvm():

    provider = cb.Assign(
        assign_to="Selected Clusters")
    provider.computeassign()

    flash.assert_message_match('Rate Assignments saved')


def rate_assignment():
    return cb.ComputeRate(assign_to="The Enterprise")


def test_assign_storage_enterprise():

    enterprise = cb.Assign(
        assign_to="The Enterprise")
    enterprise.storageassign()

    flash.assert_message_match('Rate Assignments saved')
