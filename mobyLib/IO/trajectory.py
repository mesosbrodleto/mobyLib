
from abc import ABC, abstractmethod

class DataSourceError(Exception):
   """Base class for other exceptions"""
   pass


class FeatureError(DataSourceError):
   """Raised when trajectory is missing required feature"""
   pass

class DataError(DataSourceError):
   """Raised when data is missing required feature"""
   pass




class Trajectory(ABC):
    """
    Abstract class for Trajectory document.

    A trajectory is a JSON document,
    MobyLib define a flexible format for trajectory document, with some required field and letting the user
    extend the format to fit particular needs.

    A possible format for Trajectory document is the following:

    {
    'geometry' : GEOJson document with trajectory points
    'timestamps' : list of timestamps corresponding to trajectory points.
                   Corresponding should be 1:1, one timestamp for each point

   'features' :
             {
             'tid' : trajectory identificator
             'uid' : user identificator
             '<custom feature>' : <custom value>
             }
    }


    """

    @abstractmethod
    def create_trajectory(self, input_data, stop_param, skip_ordering = False, store = None):
        """
        Function to create trajectory from input data (csv, db table, colelction etc)


        Input:
            input_data: pointer to input data
            stop_param : dictionary, parameters for stop detection (space and time from point to next one)
            time_format : string, format of datetime according to datetime library standard
            skip_ordering: boolean, set to True if input data is already ordered by uid and times
            to_file: function. If defined, trajectories are stored (using store())
            instead of returning the whole list of trajectories

        Output:
            list of trajectory documents, if store is False. Else, None is returned

        """
        return

    @abstractmethod
    def dump_trajectory(self, trajectory_data, output):
        """
        Function to store trajectories.

        Input:
            trajectory_data: pointer to trajectory documents
            output: function to store data (writing to file for CSV, writing table for db, etc)
        """

    @abstractmethod
    def load_trajectory(self, trajectory_data, output):
        """
        Function to store trajectories.

        Input:
            trajectory_data: pointer to trajectory documents
            output: function to store data (writing to file for CSV, writing table for db, etc)
        """

    @abstractmethod
    def check_trajectory(self, trajectory_data):
        """
        Function to check if input trajectory documents are compliant with the format.
        It is used to design the structure of trajectory document

        Input:
            trajectory_data: pointer to trajectory documents
        """


    @abstractmethod
    def check_mobilityData(self, input_data, template):
        """
        Check if input data is compliant with the mobility data required to create a trajectory

        Input:
            input_data: pointer to input data
            template: dictionary to specify semantics of input_data.
                    e.g. for CSV it contains columns indexes {'id':0,'lat':1, ...}

        Note: mandatory field for mobility data template are:

        uid: user identificator
        lat: latitude coordinate
        lon: longitude coordinate
        ts: timestamp coordinate

        Output: boolean
        """

        for feature in ['uid','lat','lon','ts']:
            if feature not in template:
                return False
        return True
