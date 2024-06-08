import sqlite3
import os

import config_reader as config

DB_PATH = os.path.join(config.Bot.data_folder, "User Data", "users.db")

def get_database_connection():
    return sqlite3.connect(DB_PATH)

def create_user_entry(user_id, message_count, xp, level, commands_used, reported, been_reported, nsfw_opt_out):
    nsfw_opt_out = int(nsfw_opt_out)
    try:
        with get_database_connection() as connection:
            cursor = connection.cursor()
            new_user = (user_id, message_count, xp, level, commands_used, reported, been_reported, nsfw_opt_out)
            cursor.execute('''
                INSERT INTO users (id, msg_count, xp, level, cmds_used, reported, been_reported, nsfw_opt_out) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', new_user)
            connection.commit()
            return new_user
    except sqlite3.Error as e:
        from bot import logger
        logger.error(f"Error while creating user entry: {e}")
        return None

def get_user_entry(user_id: int, values=None):
    """
    A function for getting a user entry from the database

    Args:
        user_id (int): The id of the user you want to get the entry for
        values (list os strings): Optional. A list of values you want to retrieve from the entry. If not specified, everything will be retrieved
            possible_values: (id, msg_count, xp, level, cmds_used, reported, been_reported, nsfw_opt_out)
    Returns:
        user_data (tuple): The databse entry with the specified values
        None: If the user wasn't found or there was an error
    """

    try:
        with get_database_connection() as connection:
            cursor = connection.cursor()
            if values:
                columns = ", ".join(values)
                cursor.execute(f"SELECT {columns} FROM users WHERE id = ?", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return tuple(user_data)
                else:
                    return None
            else:
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return tuple(user_data)
                else:
                    return None
    except sqlite3.Error as error:
        from bot import logger
        logger.error(f"Error while reading user entry: {error}")
        return None

def update_user_entry(user_id: int, increment: bool = True, msg_count: int = 0, xp: int = 0, level: int = 0, cmds_used: int = 0, reported: int = 0, been_reported: int = 0, nsfw_opt_out: int = None) -> bool:
    """
    A function that modifies a user entry and creates one if it doesn't exist

    Args:
        user_id: The id of the user you want to modify the entry for
        increment: If True, values will be incremented instead of replaced
        msg_count: The number of messages the user has sent
        xp: The number of xp the user has
        level: The level of the user
        cmds_used: How many commands they have used
        reported: How many times the user reported
        been_reported: How many the user has been reported
        nsfw_opt_out: If they have opted out of nsfw (None for no change, 0 for no, 1 for yes)
    Returns:
        True: Success
        False: Error
    """
    
    try:
        with get_database_connection() as connection:
            cursor = connection.cursor()
            
            if increment:
                # Increment the values
                sql = """
                    UPDATE users 
                    SET msg_count = msg_count + ?, xp = xp + ?, level = level + ?, cmds_used = cmds_used + ?, 
                        reported = reported + ?, been_reported = been_reported + ?
                """
                params = [msg_count, xp, level, cmds_used, reported, been_reported]
                if nsfw_opt_out is not None:
                    sql += ", nsfw_opt_out = ?"
                    params.append(nsfw_opt_out)
                sql += " WHERE id = ?"
                params.append(int(user_id))
                cursor.execute(sql, params)
            else:
                # Replace the values
                sql = """
                    UPDATE users 
                    SET msg_count = ?, xp = ?, level = ?, cmds_used = ?, reported = ?, been_reported = ?
                """
                params = [msg_count, xp, level, cmds_used, reported, been_reported]
                if nsfw_opt_out is not None:
                    sql += ", nsfw_opt_out = ?"
                    params.append(nsfw_opt_out)
                sql += " WHERE id = ?"
                params.append(int(user_id))
                cursor.execute(sql, params)
            
            # Commit the transaction
            connection.commit()
            return True

    except sqlite3.Error as e:
        from bot import logger
        logger.error(f"Error while updating user entry: {e}")
        return False


def update_nsfw_status(user_id: int, nsfw_opt_out: bool) -> bool:
    nsfw_opt_out = int(nsfw_opt_out)


    try:
        with get_database_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE users 
                SET nsfw_opt_out = ? 
                WHERE id = ?
            """, (nsfw_opt_out, int(user_id)))

            return True
    except Exception as e:
        from bot import logger
        logger.error(f"Error while updating nsfw status in the database: {e}")
        return False
