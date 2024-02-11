class DatabaseConnector:
    def __init__(self):
        pass

    @staticmethod
    def connect(config_data):
        import mysql.connector

        print(f"Attempting to establish connection to {config_data.get('databaseURL')}")
        cnx = mysql.connector.connect(host=config_data.get('databaseURL'),
                                      user=config_data.get('databaseUser'),
                                      password=config_data.get('databasePass'),
                                      database=config_data.get('database'),
                                      port=3306)
        print(f"#Successfully established connection to {config_data.get('databaseURL')}")

        return cnx
