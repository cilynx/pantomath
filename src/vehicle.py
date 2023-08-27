import wx
import os
import json
import wx.lib.agw.thumbnailctrl as tc

class Vehicle():
    """
    A vehicle
    """

    def __init__(self, path):
        print(f'Vehicle({path})')
        self.path = path
        with open(os.path.join(path, 'props.json'), 'r') as json_file:
            data = json.load(json_file)
            for key, value in data.items():
                setattr(self, key, value)

class VehiclePage(wx.Panel):
    """
    The Vehicles UI
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.library = parent.Parent.Parent.library
        self.vehicles = []

        for entry in os.scandir(os.path.join(self.library.dir, 'vehicles')):
            self.vehicles.append(Vehicle(entry.path))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(VehicleList(self, self.vehicles), 1, wx.EXPAND)

        self.SetSizer(sizer)

class VehicleList(wx.ListCtrl):
    def __init__(self, parent, vehicles):
        super(VehicleList, self).__init__(parent, style=wx.LC_REPORT)

        # Image list to hold vehicle images
        self.image_list = wx.ImageList(400, 225)
        self.AssignImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        # Set up columns
        self.InsertColumn(0, 'Image', width=420)
        self.InsertColumn(1, 'Year')
        self.InsertColumn(2, 'Make')
        self.InsertColumn(3, 'Model')
        self.InsertColumn(4, 'Color')
        self.InsertColumn(5, 'VIN')

        # Add the vehicles to the list
        for vehicle in vehicles:
            img = wx.Image(os.path.join(vehicle.path, 'image.png'), wx.BITMAP_TYPE_ANY).Scale(400, 225)
            img_idx = self.image_list.Add(wx.Bitmap(img))

            index = self.InsertItem(self.GetItemCount(), "", img_idx)
            self.SetItem(index, 1, str(vehicle.year))  # Convert year to string
            self.SetItem(index, 2, vehicle.make)
            self.SetItem(index, 3, vehicle.model)
            self.SetItem(index, 4, vehicle.color)
            self.SetItem(index, 5, vehicle.vin)
