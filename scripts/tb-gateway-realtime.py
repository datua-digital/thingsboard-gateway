"""Run the IoT Gateway command"""

from thingsboard_gateway.gateway.tb_gateway_service import TBGatewayService
import sys
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()
    config_file_path = sys.argv[1]
    TBGatewayService(config_file_path)
