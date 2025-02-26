#     Copyright 2022. ThingsBoard
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from time import time
from datetime import timezone

from thingsboard_gateway.connectors.opcua.opcua_converter import OpcUaConverter
from thingsboard_gateway.tb_utility.tb_utility import TBUtility
from thingsboard_gateway.gateway.statistics_service import StatisticsService


class OpcUaUplinkConverter(OpcUaConverter):
    def __init__(self, config, logger):
        self._log = logger
        self.__config = config

    @property
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        self.__config = value

    @StatisticsService.CollectStatistics(start_stat_type='receivedBytesFromDevices',
                                         end_stat_type='convertedBytesFromDevice')
    def convert(self, config, val, data=None, key=None):
        information = config[0]
        information_type = config[1]
        device_name = self.__config["deviceName"]
        result = {"deviceName": device_name,
                  "deviceType": self.__config.get("deviceType", "OPC-UA Device"),
                  "attributes": [],
                  "telemetry": [], }
        try:
            information_types = {"attributes": "attributes", "timeseries": "telemetry"}
            path = TBUtility.get_value(information["path"], get_tag=True)
            full_key = key if key else information["key"]
            full_value = information["path"].replace("${"+path+"}", str(val))
            if information_type == 'timeseries' and data is not None and not self.__config.get(
                    'subOverrideServerTime', False):
                # Note: SourceTimestamp and ServerTimestamp may be naive datetime objects, hence for the timestamp() the tz must first be overwritten to UTC (which it is according to the spec)
                if data.monitored_item.Value.SourceTimestamp is not None:
                    timestamp = int(data.monitored_item.Value.SourceTimestamp.replace(tzinfo=timezone.utc).timestamp()*1000)
                elif data.monitored_item.Value.ServerTimestamp is not None:
                    timestamp = int(data.monitored_item.Value.ServerTimestamp.replace(tzinfo=timezone.utc).timestamp()*1000)
                else:
                    timestamp = int(time()*1000)
                result[information_types[information_type]].append({"ts": timestamp, 'values': {full_key: full_value}})
            else:
                result[information_types[information_type]].append({full_key: full_value})
            return result
        except Exception as e:
            self._log.exception(e)
