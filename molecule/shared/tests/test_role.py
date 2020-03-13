import pytest

import os

import json

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('name', [
  ('sensu-go-cli'),
])
def test_packages_are_installed(host, name):
    package = host.package(name)
    assert package.is_installed


@pytest.mark.parametrize('api_url,format,namespace,username', [
  ('http://127.0.0.1:8080', 'json', 'default', 'admin'),
])
def test_sensuctl_is_configured(host, api_url, format, namespace, username):
    json_data = host.check_output('sensuctl config view')
    config = json.loads(json_data)
    assert config['api-url'] == api_url
    assert config['format'] == format
    assert config['namespace'] == namespace
    assert config['username'] == username


@pytest.mark.parametrize('name,version', [
  ('sensu-plugins-cpu-checks', '4.1.0'),
  ('sensu-ruby-runtime', '0.0.10'),
  ('sensu/sensu-slack-handler', '1.0.3'),
])
def test_assets_are_installed(host, name, version):
    json_data = host.check_output('sensuctl asset list')
    assets = json.loads(json_data)
    for asset in assets:
        metadata = asset['metadata']
        if metadata['name'] == name:
            annotations = metadata['annotations']
            assert annotations['io.sensu.bonsai.version'] == version
            break
    else:
        assert False
