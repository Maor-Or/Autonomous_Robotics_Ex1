class BatterySensor:

    def __init__(self , battery_precentage=100):
        self.battery_precentage = battery_precentage 
        # we update the value 10 times per sec , and the battrey life is 480 secs so we will decrease this value by 1 ticks per update
        self.remaining_ticks_to_battrey_life = 4800 
    '''
    this function is being called 10 times per second, in each call we decrese the remaining ticks by 1
    and update the battery precentage accordingly
    '''
    def update_battrey_precentage(self):
        remaining_ticks_to_battrey_life -= 1
        self.battery_precentage = (self.remaining_ticks_to_battrey_life / 4800) * 100 # update the battery precentage

    def get_battrey_precentage(self):
        return self.battery_precentage