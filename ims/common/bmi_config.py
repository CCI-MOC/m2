import ims.common.constants as constants


def parse_config(cfg):
    # Mandatory Options
    # BMI Section
    cfg.option(constants.BMI_SECTION, constants.UID_OPT)
    cfg.option(constants.BMI_SECTION, constants.SERVICE_OPT, type=bool)

    # DB Section
    cfg.option(constants.DB_SECTION, constants.DB_PATH_OPT)

    # RPC Section
    cfg.option(constants.RPC_SECTION, constants.RPC_SERVER_IP_OPT)
    cfg.option(constants.RPC_SECTION, constants.RPC_SERVER_PORT_OPT, type=int)
    cfg.option(constants.RPC_SECTION, constants.NAME_SERVER_IP_OPT)
    cfg.option(constants.RPC_SECTION, constants.NAME_SERVER_PORT_OPT, type=int)

    # TFTP Section
    cfg.option(constants.TFTP_SECTION, constants.PXELINUX_PATH_OPT)
    cfg.option(constants.TFTP_SECTION, constants.IPXE_PATH_OPT)

    # REST API Section
    cfg.option(constants.REST_API_SECTION, constants.REST_API_IP_OPT)
    cfg.option(constants.REST_API_SECTION, constants.REST_API_PORT_OPT,
               type=int)

    # Logs Section
    cfg.option(constants.LOGS_SECTION, constants.LOGS_PATH_OPT)
    cfg.option(constants.LOGS_SECTION, constants.LOGS_DEBUG_OPT, type=bool)
    cfg.option(constants.LOGS_SECTION, constants.LOGS_VERBOSE_OPT, type=bool)

    # Driver Section
    cfg.option(constants.DRIVER_SECTION, constants.NET_ISOLATOR_DRIVER_OPT)
    cfg.option(constants.DRIVER_SECTION, constants.ISCSI_DRIVER_OPT)
    cfg.option(constants.DRIVER_SECTION, constants.FS_DRIVER_OPT)

    # Mandatory Sections (Typically Driver Sections)
    cfg.section(constants.ISCSI_SECTION)
    cfg.section(constants.NET_ISOLATOR_SECTION)
    cfg.section(constants.FS_SECTION)

    # Optional Sections
    cfg.section(constants.TESTS_SECTION, required=False)
