# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of DataTag.
#
# DataTag is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataTag is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with DataTag.  If not, see <http://www.gnu.org/licenses/>

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Append the given tag to the given files"

    def add_arguments(self, parser):
        parser.add_argument("--tag", type=str)
        parser.add_argument("files", nargs="+", type=str)

    def handle(self, *args, **options):
        with open(".DataTag.yaml", "a") as f_conf:
            f_conf.write("- pattern: [%s]\n" % ", ".join(options["files"]))
            f_conf.write("  tags:\n")
            f_conf.write("  - %s\n" % options["tag"])
