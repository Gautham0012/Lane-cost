"""
Feature group taxonomy for the Veltris Vehicle Shipment Cost dataset.
Every retained feature (post cleaning / dimensionality reduction) is mapped to
exactly one business-meaningful group. Used for EDA-by-group, reporting, and
for explaining *why* a feature belongs where it does.
"""

FEATURE_GROUPS = {
    "Distance": [
        "TotalMiles", "HaversineMiles", "LengthOfHaul", "delta_lat", "delta_lon",
        "OriginLatitude", "OriginLongitude", "DestinationLatitude", "DestinationLongitude",
        "TotalStops", "NumberOfPick", "NumberOfDrop",
    ],
    "Equipment": [
        "EquipmentType", "Enclosed", "NetHeight", "NetLength", "NetWheelBase",
        "IsEV", "IsHybrid", "FuelTypeKnown",
        "TypePassengerCar", "TypeSUVMinivan", "TypeTruckVanSmall", "TypeTruckVanMedium",
        "TypeTruckVanLarge", "TypeMissing",
        "TotalWeight", "WeightKnown", "WeighedVehicleCount", "VehicleWeightSum",
        "VehicleWeightKnown", "VehicleWeightKnownCount", "VehicleYearMean",
        "VehicleCount", "VehicleSpecsKnown", "ItemCount",
    ],
    "Fuel Price": [
        "OriginGasPrice", "DestinationGasPrice",
        "OriginWDieselPrice", "DestinationWDieselPrice",
        "OriginMDieselPrice", "DestinationMDieselPrice",
    ],
    "Historical Lane Cost": [
        "TotalCost_min_2w_lane_zip3", "TotalCost_max_2w_lane_zip3", "TotalCost_mean_2w_lane_zip3",
        "TotalCost_count_2w_lane_zip3", "TotalCost_std_2w_lane_zip3",
        "TotalCost_min_3m_lane_state", "TotalCost_max_3m_lane_state", "TotalCost_mean_3m_lane_state",
        "TotalCost_count_3m_lane_state", "TotalCost_std_3m_lane_state",
        "TotalCost_min_6m_lane_state", "TotalCost_max_6m_lane_state", "TotalCost_mean_6m_lane_state",
        "TotalCost_count_6m_lane_state", "TotalCost_std_6m_lane_state",
        "TotalCostOriginMean", "TotalCostDestinationMean",
        "OriginZip3_TE", "DestinationZip3_TE", "TotalMiles_TE",
    ],
    "Market Conditions": [
        "AutoInventorySalesRatio", "AutoManufacturerInventoryValue", "AutoPersonalConsumptionExpenditures",
        "FreightTSIndex", "FreightTSIndexChange", "TruckTonnageIndex",
        "AutoManufacturerValueOfShipments", "AutoIPManufacturing",
        "TotalManufacturerInventoryValue", "TotalManufacturerValueofShipments",
        "TotalManufacturerInventoryShipmentsRatios", "ConsumerGoodsIndustrialProduction",
        "TruckingProducerPriceIndex", "TruckingLDProducerPriceIndex", "TotalVehicleSales",
        "CapitalGoodsManufacturersNewOrders", "LightWeightVehicleSales",
        "CapitalGoodsManufacturersValueOfShipments", "ConsumerPriceInflation",
        "AllCommoditiesProducerPriceIndex", "RecessionIndicator", "TotalBusinessInventories",
        "ChangeMatrix_InboundIndex", "ChangeMatrix_OutboundIndex",
        "Origin_RUCC_2023", "Destination_RUCC_2023",
        "Origin_Heavy_Wage", "Origin_Heavy_LQ", "Origin_Heavy_Employment", "Origin_Heavy_EmploymentPer1000",
        "Origin_Light_Wage", "Origin_Light_LQ", "Origin_Light_Employment", "Origin_Light_EmploymentPer1000",
        "Destination_Heavy_Wage", "Destination_Heavy_LQ", "Destination_Heavy_Employment",
        "Destination_Heavy_EmploymentPer1000",
        "Destination_Light_Wage", "Destination_Light_LQ", "Destination_Light_Employment",
        "Destination_Light_EmploymentPer1000",
    ],
    "Seasonality": [
        "CreationDate_is_weekend", "CreationDate_is_eoq", "CreationDate_is_holiday",
        "CreationDate_day_of_year_sin", "CreationDate_day_of_year_cos",
        "CreationDate_day_of_week_sin", "CreationDate_day_of_week_cos",
        "lead_time_days", "delivery_date_days",
    ],
    "Carrier": [
        "SourceId", "SourceName", "MarketPlaceShipment", "MarketplaceCovered",
        "Assigned", "PendingPickup", "Expedited",
    ],
    "Customer": [
        "OriginState", "DestinationState", "OriginZip3", "DestinationZip3",
        "OriginZipZone", "DestinationZipZone",
    ],
}

# Business rationale for each group -- used verbatim in the Word/PPT report.
GROUP_RATIONALE = {
    "Distance": (
        "Captures the physical geography of the move: total/haversine miles, lat-lon deltas, "
        "length of haul and the number of stops/pickups/drops along the route. Distance is the "
        "single largest structural driver of linehaul cost in trucking, so all raw and derived "
        "geographic-distance measures are grouped together."
    ),
    "Equipment": (
        "Describes the vehicle(s) being shipped and the trailer/equipment used to move them - "
        "type of equipment, enclosed vs open, dimensions (height/length/wheelbase), weight, "
        "vehicle body-type flags, EV/hybrid flags and vehicle count/age. Equipment determines "
        "capacity constraints and specialized-handling premiums, so it is priced differently from "
        "pure distance."
    ),
    "Fuel Price": (
        "Origin and destination gas/diesel (wholesale and mid-grade) prices at time of shipment. "
        "Fuel is a direct, pass-through input cost for carriers and is tracked separately from "
        "broader macro market indices because of its short-run volatility and direct linkage to "
        "carrier fuel surcharges."
    ),
    "Historical Lane Cost": (
        "Rolling historical statistics (min/max/mean/count/std) of what the same lane (zip3-to-zip3 "
        "or state-to-state) cost over the trailing 2 weeks, 3 months and 6 months, plus origin/"
        "destination mean cost and target-encoded lane identifiers. These are the strongest "
        "empirical priors for 'what should this lane cost' and are grouped separately from "
        "real-time market indices."
    ),
    "Market Conditions": (
        "Macro-economic and industry indices (freight indices, trucking PPI, manufacturing/"
        "inventory ratios, vehicle sales, recession indicator) plus regional labor-market context "
        "(RUCC rurality code, heavy/light-industry wages and employment at origin/destination). "
        "These describe the broader supply/demand backdrop for freight pricing that is outside any "
        "single shipment's control."
    ),
    "Seasonality": (
        "Calendar effects - day-of-week and day-of-year cyclical encodings, weekend/end-of-quarter/"
        "holiday flags, and lead-time / delivery-time gaps. Freight rates are known to move with "
        "weekly and yearly demand cycles independent of macro market conditions."
    ),
    "Carrier": (
        "Attributes of the platform/carrier-sourcing channel handling the shipment - source system, "
        "whether it went through a marketplace and was covered there, whether it was expedited, "
        "assigned or still pending pickup. These reflect carrier-side operational and sourcing "
        "factors rather than the physical shipment itself."
    ),
    "Customer": (
        "Origin/destination geography as experienced by the customer - state, zip3 and zip-zone. "
        "Kept separate from 'Distance' because these are categorical location identifiers (which "
        "lane/region a customer ships from or to) rather than continuous physical-distance measures."
    ),
}
