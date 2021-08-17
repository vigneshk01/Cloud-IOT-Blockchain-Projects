#Delivery routes for each city - normal delivery
NORMAL_DELIVERY_MAP_CONFIG = '../config/normal_delivery_map.txt'
#Delivery routes for each city - premium delivery
PREMIUM_DELIVERY_MAP_CONFIG = '../config/premium_delivery_map.txt'
#Order list
ORDER_BATCH_CONFIG = '../config/order_batch.txt'


# Order class stores details of a particular order and its attributes
# It also has a dispatch method to trigger delivery of the order via a specific route
class Order:
    def __init__(self, id, item_name, customer, order_date, city, delivery_date, delivery_type):
        self._id = id
        self._item_name = item_name
        self._customer = customer
        self._order_date = order_date
        self._city = city
        self._delivery_date = delivery_date
        self._delivery_type = delivery_type

    #__str__ is a special function that allows customising the information that's displayed when one prints the object
    def __str__(self):
        return f'ID - {self.id}, Item Name - {self.item_name}, Order Date - {self.order_date}, Customer - {self.customer}, City - {self.city}, Delivery Date - {self.delivery_date}, Delivery Type - {self.delivery_type}'
    
    # @property is a way of creating a getter function for internal attributes.
    # The actual attribute is named with an underscore at the beginning highlighting no direct access, by convention
    # The function should have the same name, without the underscore
    # It can be used like an attribute and python will automatically call this function to retrieve the correct value
    @property
    def id(self):
        return self._id

    @property
    def item_name(self):
        return self._item_name

    @property
    def order_date(self):
        return self._order_date

    @property
    def customer(self):
        return self._customer

    @property
    def city(self):
        return self._city

    @property
    def delivery_date(self):
        return self._delivery_date

    @property
    def delivery_type(self):
        return self._delivery_type
    

    #This will trigger a dispatch of the order using a specific delivery route. This is an example of double dispatch
    def dispatch(self, delivery_route):
        print(f'Dispatching order {order}')
        delivery_route.process_order(self)


# OrderBatch is an aggregation of order objects
# It reads in the details from the order_batch_config file and creates a list of order objects
class OrderBatch:
    def __init__(self):
        self._order_batch = []

    def __str__(self):
        pass

    def read_config(self, order_batch_config):
        # Opens the file and reads all the order rows, stripping newline character at the end
        # Using the 'with' keyword automatically closes the file when the block is finished or if an error happens
        with open(order_batch_config, 'r') as obatch_file:
            obatch_lines = [obatch_line.rstrip() for obatch_line in obatch_file]

        # An order object is created for each row, and all the order objects are aggregated in the OrderBatch object
        for order_entry in obatch_lines:
            order_details = order_entry.split('-')
            order = Order(order_details[0], order_details[1], order_details[2], order_details[3], order_details[4], order_details[5], order_details[6])  

            self._order_batch.append(order)

    def get_orders(self):
        return self._order_batch

# DeliveryMap reads from one of the delivery map files and stores destinations, and stages for each destination
class DeliveryMap:
    def __init__(self):
        self._destinations = []
        self._delivery_map = {}

    def __str__(self):
        pass

    # This method creates two structures
    # It creates a list of all the destinations found
    # It also creates a dictionary with destination as the key, and list of stages as the value
    def read_config(self, delivery_map_config):
        with open(delivery_map_config, 'r') as dmap_file:
            dmap_lines = [dmap_line.rstrip() for dmap_line in dmap_file]


        for line in dmap_lines:
            destination, stages = line.split(' ')
            self._destinations.append(destination)
            stages = stages.split(',')
            self._delivery_map[destination] = stages
        print(f'Destinations: {self._destinations}')

    def get_destinations(self):
        return self._destinations 

    def routing_map(self):
        return self._delivery_map

    def get_stages(self, delivery_center):
        return self._delivery_map[delivery_center]


# DeliveryStage is an object storing information for a specific stage of a specific route
# It'll also store the next stage in the route
class DeliveryStage:
    def __init__(self, source, destination):
        self._source = source
        self._destination = destination
        self._next_stage = None

    @property
    def next_stage(self):
        return self._next_stage

    # This is a way to create a setter for a private attribute
    # The name in the annotation and the method name should match the attribute name (without the underscore)
    # It can be used like an attribute and python will automatically call this function to assign the value
    # for example, you can say ds_object.next_stage = dfg_stage, treating it like an attribute
    # This would automatically call this function and assign the value to the internal attribute appropriately
    @next_stage.setter
    def next_stage(self, successor):
        self._next_stage = successor

    def process_order(self, order):
        pass


# TrainDispatch, FlightDispatch, and TruckDispatch override DeliveryStage.
# They specify a particular type of transport, alongwith the base source and destination attributes

class TrainDispatch(DeliveryStage):
    def __init__(self, source, destination):
        super().__init__(source, destination)

    def __str__(self):
        return f'Train from {self._source} to {self._destination}'
    
    
    def process_order(self, order):
        # This would have the actual logic of processing the train dispatch
        # The following string is a placeholder since this logic is not relevant to the project
        print(f'Order {order.id} - Train Dispatch from {self._source} to {self._destination}')

        # After processing the stage, this triggers the next stage in the route for processing
        # This is an example of the chain of responsibility pattern
        if self.next_stage:
            return self.next_stage.process_order(order)
        else:
            return None 


class FlightDispatch(DeliveryStage):
    def __init__(self, source, destination):
        super().__init__(source, destination)
    
    def __str__(self):
        return f'Flight from {self._source} to {self._destination}'
    
    
    def process_order(self, order):
        # This would have the actual logic of processing the flight dispatch
        # The following string is a placeholder since this logic is not relevant to the project
        print(f'Order {order.id} - Flight Dispatch from {self._source} to {self._destination}')

        # After processing the stage, this triggers the next stage in the route for processing
        # This is an example of the chain of responsibility pattern
        if self.next_stage:
            return self.next_stage.process_order(order)
        else:
            return None 


class TruckDispatch(DeliveryStage):
    def __init__(self, source, destination):
        super().__init__(source, destination)

    def __str__(self):
        return f'Truck from {self._source} to {self._destination}'
        
    def process_order(self, order):
        # This would have the actual logic of processing the truck dispatch
        # The following string is a placeholder since this logic is not relevant to the project
        print(f'Order {order.id} - Truck Dispatch from {self._source} to {self._destination}')

        # After processing the stage, this triggers the next stage in the route for processing
        # This is an example of the chain of responsibility pattern
        if self.next_stage:
            return self.next_stage.process_order(order)
        else:
            return None 


# DeliveryRoute stores all the stage objects for a specific route, in order
class DeliveryRoute:
    def __init__(self, stage_list, destination):
        self._stage_list = stage_list
        self._destination = destination

    def __str__(self):
        route = ','.join(str(stage) for stage in self._stage_list)
        return f'Route to {self._destination}: {route}\n'
        
    # This triggers the first stage which will, in turn, trigger the following stage and so on, until delivery finishes
    def process_order(self, order):
        self._stage_list[0].process_order(order)

# DeliverySystem is the core engine that stores all route objects mapped to the destinations
# It triggers delivery map creation and allows retrieval of a particular route based on destination
# It's an example of a builder class which handles creation of various objects and then provides access to relevant ones
class DeliverySystem:
    def __init__(self):
        self.delivery_centers = []
        self.stage_routes = {}

    def populate_route(self, center, stages):
        stage_list = []
        # This parses the stage strings and creates all stage objects
        for stage in stages:
            source, dispatch_method, destination = stage.split('-')
            if (dispatch_method == 'truck'):
                stage_list.append(TruckDispatch(source, destination))
            elif (dispatch_method == 'train'):
                stage_list.append(TrainDispatch(source, destination))
            elif (dispatch_method == 'flight'):
                stage_list.append(FlightDispatch(source, destination))

        # This adds the next stage information in each stage object, creating a chain
        for i in range(0, len(stage_list) - 1):
            stage_list[i].next_stage = stage_list[i+1]
        
        # Finally, the DeliveryRoute object is created, composing all its stages, in order
        route = DeliveryRoute(stage_list, destination)
        print(route)

        return route

    def configure(self, DELIVERY_MAP_CONFIG):
        # Creates and triggers DeliveryMap to ingest destination and stage information
        delivery_map = DeliveryMap()
        delivery_map.read_config(DELIVERY_MAP_CONFIG)

        self.delivery_centers.extend(delivery_map.get_destinations())
        
        # It goes through each destination and creates appropriate objects for stages and the route
        for center in self.delivery_centers:
            stages = delivery_map.get_stages(center)
            route = self.populate_route(center, stages)
            self.stage_routes[center] = route

    # Returns the route for a particular destination which can then be used for dispatching an order
    def get_route(self, destination):
            return self.stage_routes[destination]

        
# Client Context

# DeliverySystem object creation for normal routes, for all destinations
normal_delivery_system = DeliverySystem()
normal_delivery_system.configure(NORMAL_DELIVERY_MAP_CONFIG)

# DeliverySystem object creation for premium routes, for all destinations
premium_delivery_system = DeliverySystem()
premium_delivery_system.configure(PREMIUM_DELIVERY_MAP_CONFIG)

# Order objects and OrderBatch created based on order list in the config
order_batch = OrderBatch()
order_batch.read_config(ORDER_BATCH_CONFIG)

orders = order_batch.get_orders()

# For each order, based on the delivery type, either normal or premium delivery system is used
# The route to the order destination is then retrieved from the selected delivery system
# The order is dispatched by passing the selected route as a parameter. This in turn would trigger order processing in the route object
for order in orders:
    if (order.delivery_type == 'Normal'):
        route = normal_delivery_system.get_route(order.city)
    elif (order.delivery_type == 'Premium'):
        route = premium_delivery_system.get_route(order.city)
    order.dispatch(route)
    print('\n')