"""
Copyright 2021 dev@yata.yt

This file is part of yata.

    yata is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    yata is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with yata. If not, see <https://www.gnu.org/licenses/>.
"""

from rest_framework import serializers
from faction.models import *

class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = "__all__"

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"

class ChainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chain
        fields = "__all__"

class CountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Count
        fields = "__all__"

class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = "__all__"
