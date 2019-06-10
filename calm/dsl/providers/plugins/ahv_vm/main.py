import click
import json
from jsonschema import Draft7Validator
import re

from calm.dsl.api import get_resource_api, get_api_client
from calm.dsl.providers import get_provider_interface

from .constants import AHV as ahv


Provider = get_provider_interface()


# Implements Provider interface for AHV_VM
class AhvVmProvider(Provider):

    provider_type = "AHV_VM"
    package_name = __name__
    spec_template_file = "ahv_vm_provider_spec.yaml.jinja2"

    @classmethod
    def create_spec(cls):
        client = get_api_client()
        create_ahv_spec(client)


class AHV:
    def __init__(self, connection):
        self.connection = connection

    def images(self):
        Obj = get_resource_api(ahv.IMAGES, self.connection)
        return Obj.get_name_uuid_map()

    def subnets(self):
        Obj = get_resource_api(ahv.SUBNETS, self.connection)
        return Obj.get_name_uuid_map()

    def groups(self, payload):
        Obj = get_resource_api(ahv.GROUPS, self.connection)

        if not payload:
            raise Exception("no payload")

        return Obj.create(payload)

    def categories(self):

        payload = {
            "entity_type": "category",
            "filter_criteria": "name!=CalmApplication;name!=CalmDeployment;name!=CalmService;name!=CalmPackage",
            "grouping_attribute": "abac_category_key",
            "group_sort_attribute": "name",
            "group_count": 60,
            "group_attributes": [
                {"attribute": "name", "ancestor_entity_type": "abac_category_key"}
            ],
            "group_member_count": 1000,
            "group_member_offset": 0,
            "group_member_sort_attribute": "value",
            "group_member_attributes": [{"attribute": "value"}],
            "query_name": "prism:CategoriesQueryModel",
        }

        response, err = self.groups(payload)
        categories = []

        if err:
            raise Exception("[{}] - {}".format(err["code"], err["error"]))

        response = response.json()
        for group in response["group_results"]:

            key = group["group_summaries"]["sum:name"]["values"][0]["values"][0]

            for entity in group["entity_results"]:
                value = entity["data"][0]["values"][0]["values"][0]
                categories.append({"key": key, "value": value})

        return categories


def highlight_text(text, **kwargs):
    """Highlight text in our standard format"""
    return click.style("{}".format(text), fg="blue", bold=False, **kwargs)


def create_ahv_spec(client):

    spec = {}
    Obj = AHV(client.connection)
    schema = AhvVmProvider.get_provider_spec()
    path = []  # Path to the key
    option = []  # Any option occured during finding key

    click.echo("")
    path.append("name")
    spec["name"] = get_field(schema, path, option)

    choice = click.prompt(highlight_text("\nWant to add some categories(y/n)"), default="n")
    if choice[0] == "y":
        categories = Obj.categories()
        click.echo("\n Choose from given categories: \n")

        for ind, group in enumerate(categories):
            click.echo(
                "\t {}. {}:{} ".format(str(ind + 1), group["key"], group["value"])
            )

        result = {}
        while True:

            while True:
                index = click.prompt("\nEnter the index of category", default=1)
                if index > len(categories):
                    click.echo("Invalid index !!! ")

                else:
                    break

            group = categories[index]
            key = group["key"]
            if result.get(key) is not None:
                click.echo(
                    "Category corresponding to key {} already exists ".format(key)
                )
                choice = click.prompt("\nWant to replace old one (y/n)", default="n")
                if choice[0] == "y":
                    result[key] = group["value"]
                    click.echo(highlight_text("category with (key = {}) updated". format(key)))

            else:
                result[key] = group["value"]

            choice = click.prompt(
                highlight_text("\nWant to add more categories (y/n)"),
                default="n"
            )
            if choice[0] == "n":
                break

        spec["categories"] = result

    spec["resources"] = {}
    path[-1] = "resources"
    click.echo("")

    path.append("num_vcpus_per_socket")
    spec["resources"]["num_vcpus_per_socket"] = get_field(
        schema, path, option, type=int
    )

    path[-1] = "num_sockets"
    spec["resources"]["num_sockets"] = get_field(schema, path, option, type=int)

    path[-1] = "memory_size_mib"
    spec["resources"]["memory_size_mib"] = get_field(schema, path, option, type=int)

    click.echo(highlight_text("\nEnter the details of disks : \n"))

    imagesNameUUIDMap = Obj.images()
    images = list(imagesNameUUIDMap.keys())
    click.echo("Choose from given images: \n")
    for ind, name in enumerate(images):
        click.echo("\t {}. {}".format(str(ind + 1), name))

    spec["resources"]["disk_list"] = []
    path[-1] = "disk_list"
    option.append("AHV Disk List")

    adapterNameIndexMap = {}
    while True:
        image = {}

        while True:
            res = click.prompt("\nEnter the index of image", default=1)
            if res > len(images):
                click.echo("Invalid index !!! ")

            else:
                image["name"] = images[res - 1]
                click.echo("{} selected". format(highlight_text(image["name"])))
                break

        click.echo("\nChoose from given Device Types :")
        device_types = list(ahv.DEVICE_TYPES.keys())
        for index, device_type in enumerate(device_types):
            click.echo("\t{}. {}". format(index + 1, highlight_text(device_type)))

        while True:
            res = click.prompt("\nEnter the index for Device Type", default=1)
            if res > len(device_types):
                click.echo("Invalid index !!! ")

            else:
                image["device_type"] = ahv.DEVICE_TYPES[device_types[res - 1]]
                click.echo("{} selected". format(highlight_text(image["device_type"])))
                break

        click.echo("\nChoose from given Device Bus :")
        device_bus_list = list(ahv.DEVICE_BUS.keys())
        for index, device_bus in enumerate(device_bus_list):
            click.echo("\t{}. {}". format(index + 1, highlight_text(device_bus)))

        while True:
            res = click.prompt("\nEnter the index for Device Bus", default=1)
            if res > len(device_bus_list):
                click.echo("Invalid index !!! ")

            else:
                image["adapter_type"] = ahv.DEVICE_BUS[device_bus_list[res - 1]]
                click.echo("{} selected". format(highlight_text(image["adapter_type"])))
                break

        image["bootable"] = click.prompt("\nIs it bootable(y/n)", default="y")

        if not adapterNameIndexMap.get(image["adapter_type"]):
            adapterNameIndexMap[image["adapter_type"]] = 0

        disk = {
            "data_source_reference": {
                "name": image["name"],
                "kind": "image",
                "uuid": imagesNameUUIDMap.get(image["name"]),
            },
            "device_properties": {
                "device_type": image["device_type"],
                "disk_address": {
                    "device_index": adapterNameIndexMap[image["adapter_type"]],
                    "adapter_type": image["adapter_type"],
                },
            },
        }

        if image["bootable"]:
            spec["resources"]["boot_config"] = {
                "boot_device": {
                    "disk_address": {
                        "device_index": adapterNameIndexMap[image["adapter_type"]],
                        "adapter_type": image["adapter_type"],
                    }
                }
            }

        adapterNameIndexMap[image["adapter_type"]] += 1
        spec["resources"]["disk_list"].append(disk)

        choice = click.prompt(highlight_text("\nWant to add more disks(y/n)"), default="n")
        if choice[0] == "n":
            break

    choice = click.prompt(highlight_text("\nWant any virtual disks(y/n)"), default="n")
    click.echo("")

    if choice[0] == "y":
        option[-1] = "AHV VDisk List"

        while True:
            vdisk = {}

            click.echo("\nChoose from given Device Types: ")
            device_types = list(ahv.DEVICE_TYPES.keys())
            for index, device_type in enumerate(device_types):
                click.echo("\t{}. {}". format(index + 1, highlight_text(device_type)))

            while True:
                res = click.prompt("\nEnter the index for Device Type", default=1)
                if res > len(device_types):
                    click.echo("Invalid index !!! ")

                else:
                    vdisk["device_type"] = ahv.DEVICE_TYPES[device_types[res - 1]]
                    click.echo("{} selected". format(highlight_text(vdisk["device_type"])))
                    break

            click.echo("\nChoose from given Device Bus :")
            device_bus_list = list(ahv.DEVICE_BUS.keys())
            for index, device_bus in enumerate(device_bus_list):
                click.echo("\t{}. {}". format(index + 1, highlight_text(device_bus)))

            while True:
                res = click.prompt("\nEnter the index for Device Bus: ", default=1)
                if res > len(device_bus_list):
                    click.echo("Invalid index !!! ")

                else:
                    vdisk["adapter_type"] = ahv.DEVICE_BUS[device_bus_list[res - 1]]
                    click.echo("{} selected". format(highlight_text(vdisk["adapter_type"])))
                    break

            path.append("disk_size_mib")
            click.echo("")
            vdisk["size"] = get_field(schema, path, option, type=int)

            if not adapterNameIndexMap.get(vdisk["adapter_type"]):
                adapterNameIndexMap[vdisk["adapter_type"]] = 0

            disk = {
                "device_properties": {
                    "device_type": vdisk["device_type"],
                    "disk_address": {
                        "device_index": adapterNameIndexMap[vdisk["adapter_type"]],
                        "adapter_type": vdisk["adapter_type"],
                    },
                },
                "disk_size_mib": vdisk["size"],
            }

            spec["resources"]["disk_list"].append(disk)
            path = path[:-1]

            choice = click.prompt(highlight_text("\nWant to add more disks(y/n)"), default="n")
            click.echo("")
            if choice[0] == "n":
                break

    choice = click.prompt(highlight_text("Want any network adapters(y/n)"), default="n")

    if choice[0] == "y":
        subnetNameUUIDMap = Obj.subnets()
        nics = list(subnetNameUUIDMap.keys())

        click.echo("\nChoose from given subnets : \n")
        for ind, name in enumerate(nics):
            click.echo("\t {}. {}".format(str(ind + 1), name))

        spec["resources"]["nic_list"] = []

        while True:

            while True:
                res = click.prompt(
                    "\nEnter the index of subnet's name", default=1
                )
                if res > len(nics):
                    click.echo("Invalid index !!!")

                else:
                    nic = nics[res - 1]
                    click.echo("{} selected". format(highlight_text(nic)))
                    break

            nic = {
                "subnet_reference": {
                    "kind": "subnet",
                    "name": nic,
                    "uuid": subnetNameUUIDMap[nic],
                }
            }

            spec["resources"]["nic_list"].append(nic)

            choice = click.prompt(
                highlight_text("\nWant to add more network adpaters(y/n)"),
                default="n"
            )
            if choice[0] == "n":
                break

    path = ["resources"]
    option = []
    choice = click.prompt(highlight_text("\nWant to add Customization script (y/n)"), default="n")

    if choice[0] == "y":
        path.append("guest_customization")
        script_types = ahv.GUEST_CUSTOMIZATION_SCRIPT_TYPES

        click.echo("\nBelow are the script types ")
        for index, scriptType in enumerate(script_types):
            click.echo("\t {}. {}".format(str(index + 1), scriptType))

        while True:
            index = click.prompt("\nEnter the index for type of script", default=1)
            if index > len(script_types):
                click.echo("Invalid index !!!")
            else:
                script_type = script_types[index - 1]
                click.echo("{} selected\n". format(highlight_text(script_type)))
                break

        if script_type == "cloud_init":
            option.append("AHV CLOUD INIT Script")
            path = path + ["cloud_init", "user_data"]

            user_data = get_field(schema, path, option)
            spec["resources"]["guest_customization"] = {
                "cloud_init": {"user_data": user_data}
            }

        elif script_type == "sysprep":
            option.append("AHV Sys Prep Script")
            path.append("sysprep")
            script = {}

            path.append("unattend_xml")
            script["unattend_xml"] = get_field(schema, path, option)

            path[-1] = "install_type"
            script["install_type"] = get_field(schema, path, option)

            spec["resources"]["guest_customization"] = {
                "sysprep": {
                    "unattend_xml": script["unattend_xml"],
                    "install_type": script["install_type"],
                }
            }

    AhvVmProvider.validate_spec(spec)  # Final validation (Insert some default's value)
    click.echo("\nCreate spec \n")
    click.echo(highlight_text(json.dumps(spec, sort_keys=True, indent=4)))


def find_schema(schema, path, option):
    if len(path) == 0:
        return {}

    indPath = 0
    indOpt = 0

    pathLength = len(path)

    while indPath < pathLength:

        if schema.get("anyOf") is not None:

            resDict = None
            for optionDict in schema["anyOf"]:
                if optionDict["title"] == option[indOpt]:
                    resDict = optionDict
                    break

            if not resDict:
                print("Not a valid key")

            else:
                schema = resDict
                indOpt = indOpt + 1

        elif schema["type"] == "array":
            schema = schema["items"]

        else:
            schema = schema["properties"]
            schema = schema[path[indPath]]
            indPath = indPath + 1

    return schema


def validate_field(schema, path, options, spec):

    keySchema = find_schema(schema, path, options)
    return Draft7Validator(keySchema).is_valid(spec)


def get_field(schema, path, options, type=str, msg=None):

    field = path[-1]
    field = field.replace("_", " ")
    field = re.sub(r"(?<=\w)([A-Z])", r" \1", field)
    field = field.capitalize()

    if msg is None:
        msg = "Enter {}".format(field)

    data = ""
    while True:
        data = click.prompt(msg, type=type)

        if not validate_field(schema, path, options, data):
            click.echo("data incorrect. Enter again")

        else:
            break

    return data
