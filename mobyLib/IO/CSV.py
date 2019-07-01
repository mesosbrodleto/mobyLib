from .trajectory import Trajectory
from ..utils import distances

from geojson import LineString
from datetime import datetime



class Trajectory(Trajectory):

    def create_trajectory(self,stop_param, time_format, skip_ordering = False, store = False):
        """
        trajectory creation from input CSV file

        input:
            input_data: file cursor
        """

        point_data = [x.split(self.separator) for x in open(self.input_file).readlines()]
        #check points for error
        for point in point_data:
            self.check_mobilityData([point],self.template)

        if not skip_ordering :
            input_data = sorted(input_data, key = lambda x: (x[self.template['uid']],
                                                            x[self.template['ts']]))
        trajectory = []
        user = None
        trajectory_documents = []
        for point in input_data:
            uid = point[self.template['uid']]
            lat = point[self.template['lat']]
            lon = point[self.template['lon']]
            ts = datetime.strftime(point[self.template['ts']],time_format)
            # additional_keys
            custom_features = {k:point[self.template[k]] for k in self.template if k not in ['uid','tid','lat','lon','ts']}

            if user is None:
                #first point
                user = uid
                data = [uid,lat,lon,ts] + [custom_features[k] for k in sorted(custom_fetures.keys())]
                trajectory.append(data)
            elif user != uid:
                #new user

                user = uid
                data = [uid,lat,lon,ts] + [custom_features[k] for k in sorted(custom_fetures.keys())]
                trajectory = [data]
            else:
                #iter over points, check for stops
                prev_point = trajectory[-1]
                distance = distances.haversine_np(prev_point[1:3],(lat,lon))
                time_diff = ts - prev_point[3]
                if distance > stop_param['distance'] or time > stop_param['time']:
                    #trajectory cut
                    document = {}
                    document['geometry'] = Linestring([x[1:3] for x in trajectory])
                    document['timestamps'] = [x[3] for x in trajectory]
                    document['features'] = {'uid':user,'tid':len(trajectory_documents)}
                    document['features'].update(custom_fetures)
                    trajectory_documents.append(trajectory)

                    #start new trajectory
                    data = [uid,lat,lon,ts] + [custom_features[k] for k in sorted(custom_fetures.keys())]
                    trajectory = [data]
                else:
                    # adding to  current trajectory
                    data = [uid,lat,lon,ts] + [custom_features[k] for k in sorted(custom_fetures.keys())]
                    trajectory.append(data)

        return trajectory_documents
    def check_mobilityData(self, input_data, template):
        """
        check if the input_data contains valid mobility data point

        input:
            input_data: list  of points

        output:
            return False if input_data has at least one invalid item

        """

        if not super().check_mobilityData(template):
            #checking for required features
            raise DataError("missing required features (uid,lat,lon,ts)")


        for point in input_data:
            for feature in header:
                if point[header[feature]] is None:

                    raise DataError("feature",feature," is not valid")
        return True

    def check_trajectory(self, trajectory_data):
        """
        check if input trajectories are valid
        """

        for trajectory in trajectory_data:
            if 'geometry' not in trajectory:
                raise FeatureError("missing geometry")
            if 'timestamps' not in trajectory or len(trajectory['geometry'].coordinates) != len(timestamps):
                raise FeatureError("missing timestamps")
            if 'features' not in trajectory:
                raise FeatureError("missing features for trajectory")

    def load_trajectory(self, trajectory_data, input):
        """
        load previously saved trajectories from csv
        format is the following;
        uid,tid,lat,lon,ts,custom features

        """
        user = None
        trajectory_documents = []
        trajectory = []
        with open(input) as f:

            traj_data = [x.split(",") for x in f.readlines()]

            header = traj_data[0]
            traj_data = data[1:]
            for data in traj_data:
                if user is None:
                    #first line
                    user = data[0]
                    tid =  data[1]
                    trajectory.append(data)
                else:
                    if data[0]!=user:
                        #new user found, cut current trajectory

                        document['geometry'] = Linestring([x[1:3] for x in trajectory])
                        document['timestamps'] = [x[3] for x in trajectory]
                        document['features'] = {'uid':user,'tid':tid}
                        custom_features = {header[i] : data[i] for i in range(4,len(data))}
                        document['features'].update(custom_fetures)
                        trajectory_documents.append(document)

                        #start new traj
                        user = data[0]
                        tid = data[1]
                        trajectory = [data]

                    elif tid!=data[1]:
                        document = {}
                        document['geometry'] = Linestring([x[1:3] for x in trajectory])
                        document['timestamps'] = [x[3] for x in trajectory]
                        document['features'] = {'uid':user,'tid':tid}
                        custom_features = {header[i] : data[i] for i in range(4,len(data))}
                        document['features'].update(custom_fetures)
                        trajectory_documents.append(document)
                        tid=data[1]

                        trajectory = [data]
                    else:
                        #add data to current trajectory
                        trajectory.append(data)
        return trajectory_documents


    def dump_trajectory(self, trajectory_data, output):
        """
        store trajectory into specified output file.
        format is the following;
        uid,tid,lat,lon,ts,custom features

        """

        with open(output) as f:
            header = "uid,tid,lat,lon,ts"
            additional_keys = sorted([k for k in trajectory['features'] if k not in ['uid','tid']])
            header += ",".join(additional_keys)
            for tn, trajectory in enumerate(trajectory_data):
                #format csv string
                user_id = trajectory['features']['uid']
                traj_id = trajectory['features']['tid']
                line = "%s,%s"%(user_id,traj_id)
                for i,point in enumerate(trajectory['geometry']['coordinates']):
                    ts = trajectory['timestamps'][i]
                    line.append(",%s,%s,%s"%(point[0],point[1],ts))


                for k in additional_keys:
                    line.append(",%s"%trajectory['features'][k])
                if tn == 0: #print header
                    header += ",".join(additional_keys)
                    print (header, file = f)
                print (line, file=f)



    def __init__(self, file_path, separator, template):
        self.input_file = file_path
        self.template = template
        self.separator = separator
