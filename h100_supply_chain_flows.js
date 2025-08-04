// H100 GPU Complete Supply Chain Flows for Globe Visualization
// Generated from CSV data analysis - ALL supply chain relationships mapped

const H100_SUPPLY_CHAIN_FLOWS = [
    // ========== TIER 1 TO FINAL ASSEMBLY ==========
    {
        from_country: "Taiwan",
        to_country: "Global", // Final assembly location not specified
        from_lat: 23.1181,
        from_lon: 120.2625,
        to_lat: 37.4419, // Using Silicon Valley as proxy for NVIDIA
        to_lon: -122.1430,
        trade_value: 15000000000, // $15B - GPU die is highest value component
        commodity: "TSMC 4N 5nm 819 mm² Die",
        company: "Taiwan Semiconductor Mfg. → NVIDIA",
        flow_type: "core_silicon"
    },
    {
        from_country: "South Korea",
        to_country: "Global",
        from_lat: 37.1436,
        from_lon: 127.484,
        to_lat: 37.4419,
        to_lon: -122.1430,
        trade_value: 8000000000, // $8B - HBM3 memory stack
        commodity: "SK Hynix HBM3 8‑Hi (16 GB) Stack",
        company: "SK Hynix → NVIDIA",
        flow_type: "memory"
    },
    {
        from_country: "Singapore",
        to_country: "Global",
        from_lat: 1.3571,
        from_lon: 103.9588,
        to_lat: 37.4419,
        to_lon: -122.1430,
        trade_value: 2000000000, // $2B - CoWoS interposer
        commodity: "40 nm 2.5D Interposer (858 mm²)",
        company: "UMC (for TSMC CoWoS) → NVIDIA",
        flow_type: "packaging"
    },
    {
        from_country: "Japan",
        to_country: "Global",
        from_lat: 35.3697,
        from_lon: 136.612,
        to_lat: 37.4419,
        to_lon: -122.1430,
        trade_value: 1500000000, // $1.5B - Package substrate
        commodity: "ABF Substrate 20-layer class",
        company: "Ibiden Co. → NVIDIA",
        flow_type: "substrate"
    },
    {
        from_country: "Taiwan",
        to_country: "Global",
        from_lat: 22.616,
        from_lon: 120.313,
        to_lat: 37.4419,
        to_lon: -122.1430,
        trade_value: 500000000, // $500M - VRM system
        commodity: "12-phase VRM assembly",
        company: "Foxconn → NVIDIA",
        flow_type: "power_management"
    },
    {
        from_country: "Japan",
        to_country: "Global",
        from_lat: 35.365,
        from_lon: 136.602,
        to_lat: 37.4419,
        to_lon: -122.1430,
        trade_value: 300000000, // $300M - Main PCB
        commodity: "32-layer HDI PCB",
        company: "Ibiden → NVIDIA",
        flow_type: "pcb"
    },
    {
        from_country: "Japan",
        to_country: "Global",
        from_lat: 36.742,
        from_lon: 138.369,
        to_lat: 37.4419,
        to_lon: -122.1430,
        trade_value: 200000000, // $200M - Heat spreader
        commodity: "Ni-plated C1100 Cu Lid",
        company: "Shinko Electric Industries → NVIDIA",
        flow_type: "thermal_management"
    },

    // ========== TIER 2 TO TIER 1 FLOWS ==========
    
    // VRM Component Flows to Foxconn VRM Assembly
    {
        from_country: "Malaysia",
        to_country: "Taiwan",
        from_lat: 2.913,
        from_lon: 101.469,
        to_lat: 22.616,
        to_lon: 120.313,
        trade_value: 100000000, // $100M - Smart power stage
        commodity: "Renesas ISL99390",
        company: "Renesas Electronics → Foxconn",
        flow_type: "power_component"
    },
    {
        from_country: "Japan",
        to_country: "Taiwan",
        from_lat: 39.3303,
        from_lon: 139.915,
        to_lat: 22.616,
        to_lon: 120.313,
        trade_value: 80000000, // $80M - Inductor bank
        commodity: "0.33 uH Shielded Power Inductors",
        company: "TDK Corporation → Foxconn",
        flow_type: "magnetic_component"
    },
    {
        from_country: "Japan",
        to_country: "Taiwan",
        from_lat: 35.999,
        from_lon: 136.188,
        to_lat: 22.616,
        to_lon: 120.313,
        trade_value: 60000000, // $60M - MLCC bank
        commodity: "0603 22 µF X6S MLCCs",
        company: "Murata Manufacturing → Foxconn",
        flow_type: "passive_component"
    },
    {
        from_country: "Japan",
        to_country: "Taiwan",
        from_lat: 36.397,
        from_lon: 140.535,
        to_lat: 22.616,
        to_lon: 120.313,
        trade_value: 40000000, // $40M - PWM controller
        commodity: "Renesas RAA229131",
        company: "Renesas Electronics → Foxconn",
        flow_type: "control_ic"
    },
    {
        from_country: "Japan",
        to_country: "Taiwan",
        from_lat: 34.927,
        from_lon: 135.696,
        to_lat: 22.616,
        to_lon: 120.313,
        trade_value: 30000000, // $30M - Bulk capacitors
        commodity: "330 µF 9 mΩ Polymer Caps",
        company: "Panasonic Electronic Components → Foxconn",
        flow_type: "capacitor"
    },

    // PCB Component Flows to Ibiden Main PCB
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 34.958,
        from_lon: 136.613,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 50000000, // $50M - High-freq laminate
        commodity: "Megtron 6 laminate",
        company: "Panasonic Industry → Ibiden",
        flow_type: "laminate"
    },
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 35.97,
        from_lon: 139.6,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 40000000, // $40M - Copper foil
        commodity: "18 µm ED foil",
        company: "Mitsui Mining & Smelting → Ibiden",
        flow_type: "copper_foil"
    },
    {
        from_country: "Canada",
        to_country: "Japan",
        from_lat: 46.493,
        from_lon: -80.995,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 20000000, // $20M - Nickel plating
        commodity: "Electroless Ni plating",
        company: "Glencore → Ibiden",
        flow_type: "surface_finish"
    },
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 40.968,
        from_lon: -116.367,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 15000000, // $15M - Gold plating
        commodity: "Immersion Au plating",
        company: "Barrick Gold → Ibiden",
        flow_type: "precious_metal"
    },
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 39.163,
        from_lon: -119.767,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 25000000, // $25M - Solder mask
        commodity: "PSR-4000 AUS5 LPI Green",
        company: "Taiyo Ink Mfg. → Ibiden",
        flow_type: "solder_mask"
    },
    {
        from_country: "Germany",
        to_country: "Japan",
        from_lat: 52.513,
        from_lon: 13.392,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 18000000, // $18M - Via plating
        commodity: "Acid Cu Plating Solution",
        company: "Atotech → Ibiden",
        flow_type: "plating_chemistry"
    },
    {
        from_country: "China",
        to_country: "Japan",
        from_lat: 22.659,
        from_lon: 114.047,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 35000000, // $35M - LGA connector
        commodity: "988-pad LGA Socket",
        company: "Foxconn Interconnect Tech. → Ibiden",
        flow_type: "connector"
    },
    {
        from_country: "Thailand",
        to_country: "Japan",
        from_lat: 13.69,
        from_lon: 101.078,
        to_lat: 35.365,
        to_lon: 136.602,
        trade_value: 10000000, // $10M - EEPROM/sensor
        commodity: "Microchip AT24C04 + PMBus Temp",
        company: "Microchip Technology → Ibiden",
        flow_type: "sensor_ic"
    },

    // Package Substrate Component Flows to Ibiden Substrate
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 36.197,
        from_lon: 139.281,
        to_lat: 35.3697,
        to_lon: 136.612,
        trade_value: 200000000, // $200M - ABF film
        commodity: "ABF GX-92 Film 25 µm",
        company: "Ajinomoto Fine-Techno → Ibiden",
        flow_type: "dielectric_film"
    },
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 38.439,
        from_lon: 140.401,
        to_lat: 35.3697,
        to_lon: 136.612,
        trade_value: 150000000, // $150M - Solder bumps
        commodity: "SAC305 C4 Bumps Ø95 µm",
        company: "Senju Metal Industry → Ibiden",
        flow_type: "solder_bump"
    },
    {
        from_country: "Taiwan",
        to_country: "Japan",
        from_lat: 24.954,
        from_lon: 121.226,
        to_lat: 35.3697,
        to_lon: 136.612,
        trade_value: 80000000, // $80M - Underfill
        commodity: "Loctite UF1173 Capillary Underfill",
        company: "Henkel Electronic Materials → Ibiden",
        flow_type: "underfill"
    },

    // Thermal Management Flows to Shinko
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 43.107,
        from_lon: -75.252,
        to_lat: 36.742,
        to_lon: 138.369,
        trade_value: 50000000, // $50M - Indium solder
        commodity: "Indium 97 / Ag 3 Foil",
        company: "Indium Corporation → Shinko Electric",
        flow_type: "thermal_interface"
    },
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 36.391,
        from_lon: 139.06,
        to_lat: 36.742,
        to_lon: 138.369,
        trade_value: 40000000, // $40M - Graphite pad
        commodity: "Sarcon XR-m Graphite Pad",
        company: "Fujipoly → Shinko Electric",
        flow_type: "thermal_pad"
    },

    // ========== TIER 3 TO TIER 2 FLOWS ==========
    
    // Smart Power Stage Component Flows
    {
        from_country: "Japan",
        to_country: "Malaysia",
        from_lat: 32.708,
        from_lon: 130.636,
        to_lat: 2.913,
        to_lon: 101.469,
        trade_value: 50000000, // $50M - BCD-MOSFET die
        commodity: "110 nm BCDMOS die",
        company: "Renesas Electronics → Renesas Malaysia",
        flow_type: "semiconductor_die"
    },
    {
        from_country: "South Korea",
        to_country: "Malaysia",
        from_lat: 35.54,
        from_lon: 129.32,
        to_lat: 2.913,
        to_lon: 101.469,
        trade_value: 30000000, // $30M - Leadframe
        commodity: "C194 CuNiSi strip",
        company: "Poongsan → Renesas Malaysia",
        flow_type: "leadframe"
    },
    {
        from_country: "China",
        to_country: "Malaysia",
        from_lat: 31.303,
        from_lon: 120.587,
        to_lat: 2.913,
        to_lon: 101.469,
        trade_value: 20000000, // $20M - Mold compound
        commodity: "EME-G700 epoxy",
        company: "Sumitomo Bakelite → Renesas Malaysia",
        flow_type: "molding_compound"
    },
    {
        from_country: "Peru",
        to_country: "Malaysia",
        from_lat: -15.843,
        from_lon: -69.995,
        to_lat: 2.913,
        to_lon: 101.469,
        trade_value: 15000000, // $15M - Tin plating
        commodity: "Tin (Sn) finish",
        company: "Minsur → Renesas Malaysia",
        flow_type: "plating_material"
    },

    // Ferrite Core Component Flows
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 38.728,
        from_lon: 140.39,
        to_lat: 39.3303,
        to_lon: 139.915,
        trade_value: 25000000, // $25M - Ferrite powder
        commodity: "MnZn Ferrite Powder",
        company: "JFE Mineral & Alloy → TDK",
        flow_type: "ferrite_material"
    },
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 35.1,
        from_lon: 136.6,
        to_lat: 39.3303,
        to_lon: 139.915,
        trade_value: 20000000, // $20M - Copper windings
        commodity: "Ø0.10 mm E-Cu Magnet Wire",
        company: "Furukawa Electric → TDK",
        flow_type: "magnet_wire"
    },

    // MLCC Component Flows
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 35.999,
        from_lon: 136.188,
        to_lat: 35.999,
        to_lon: 136.188,
        trade_value: 40000000, // $40M - Dielectric sheets
        commodity: "Barium-Titanate Green Tape",
        company: "Murata Manufacturing (internal)",
        flow_type: "dielectric_material"
    },
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 33.25,
        from_lon: 131.7,
        to_lat: 35.999,
        to_lon: 136.188,
        trade_value: 30000000, // $30M - Electrode paste
        commodity: "Ni Electrode Screen-Print Paste",
        company: "JX Metals → Murata",
        flow_type: "electrode_material"
    },

    // PCB Laminate Component Flows
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 34.958,
        from_lon: 136.613,
        to_lat: 34.958,
        to_lon: 136.613,
        trade_value: 25000000, // $25M - Resin system
        commodity: "Low-Df epoxy blend",
        company: "Panasonic Industry (internal)",
        flow_type: "resin_system"
    },
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 33.561,
        from_lon: -81.721,
        to_lat: 34.958,
        to_lon: 136.613,
        trade_value: 35000000, // $35M - Glass fabric
        commodity: "E-glass cloth",
        company: "Owens Corning → Panasonic",
        flow_type: "glass_fabric"
    },

    // Solder Mask Component Flows
    {
        from_country: "USA",
        to_country: "USA",
        from_lat: 28.96,
        from_lon: -95.36,
        to_lat: 39.163,
        to_lon: -119.767,
        trade_value: 15000000, // $15M - Epoxy resin
        commodity: "Novolac-type epoxy",
        company: "Dow Chemical → Taiyo Ink",
        flow_type: "polymer_resin"
    },

    // Via Plating Component Flows
    {
        from_country: "Germany",
        to_country: "Germany",
        from_lat: 53.55,
        from_lon: 9.99,
        to_lat: 52.513,
        to_lon: 13.392,
        trade_value: 12000000, // $12M - Copper sulfate
        commodity: "CuSO₄ electrolyte grade",
        company: "Aurubis → Atotech",
        flow_type: "plating_salt"
    },

    // ========== TIER 4+ RAW MATERIAL FLOWS ==========
    
    // Silicon Wafer Flows
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 37.13,
        from_lon: 140.35,
        to_lat: 32.708,
        to_lon: 130.636,
        trade_value: 80000000, // $80M - Silicon wafers
        commodity: "200 mm polished wafer",
        company: "Shin-Etsu Handotai → Renesas",
        flow_type: "silicon_wafer"
    },

    // High-Purity Quartz Flows
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 35.916,
        from_lon: -82.066,
        to_lat: 37.13,
        to_lon: 140.35,
        trade_value: 100000000, // $100M - HPQ for wafers
        commodity: "HPQ ore",
        company: "The Quartz Corp → Shin-Etsu Handotai",
        flow_type: "raw_quartz"
    },
    {
        from_country: "USA",
        to_country: "USA",
        from_lat: 35.916,
        from_lon: -82.066,
        to_lat: 33.561,
        to_lon: -81.721,
        trade_value: 60000000, // $60M - Silica sand for glass
        commodity: "Quartz sand",
        company: "The Quartz Corp → Owens Corning",
        flow_type: "silica_sand"
    },

    // Copper Ore Flows
    {
        from_country: "Chile",
        to_country: "South Korea",
        from_lat: -24.272,
        from_lon: -69.072,
        to_lat: 35.54,
        to_lon: 129.32,
        trade_value: 120000000, // $120M - Copper cathode
        commodity: "99.99 % Cu cathode",
        company: "BHP → Poongsan",
        flow_type: "copper_cathode"
    },
    {
        from_country: "Chile",
        to_country: "Chile",
        from_lat: -24.272,
        from_lon: -69.072,
        to_lat: -24.272,
        to_lon: -69.072,
        trade_value: 50000000, // $50M - Copper ore processing
        commodity: "Run-of-mine ore",
        company: "BHP Escondida (mining to processing)",
        flow_type: "copper_ore"
    },
    {
        from_country: "Chile",
        to_country: "Japan",
        from_lat: -22.88,
        from_lon: -69.4,
        to_lat: 35.1,
        to_lon: 136.6,
        trade_value: 80000000, // $80M - Copper for magnet wire
        commodity: "99.99 % Cu cathode",
        company: "Freeport-McMoRan → Furukawa Electric",
        flow_type: "copper_cathode"
    },
    {
        from_country: "Chile",
        to_country: "Chile",
        from_lat: -22.88,
        from_lon: -69.4,
        to_lat: -22.88,
        to_lon: -69.4,
        trade_value: 40000000, // $40M - El Abra ore processing
        commodity: "El Abra run-of-mine ore",
        company: "Freeport-McMoRan (mining to processing)",
        flow_type: "copper_ore"
    },
    {
        from_country: "Poland",
        to_country: "Germany",
        from_lat: 51.4,
        from_lon: 16.2,
        to_lat: 53.55,
        to_lon: 9.99,
        trade_value: 70000000, // $70M - Copper concentrate
        commodity: "Lubin concentrate",
        company: "KGHM Polska Miedź → Aurubis",
        flow_type: "copper_concentrate"
    },

    // Rare Earth and Critical Materials
    {
        from_country: "Australia",
        to_country: "Japan",
        from_lat: -13.88,
        from_lon: 136.6,
        to_lat: 38.728,
        to_lon: 140.39,
        trade_value: 90000000, // $90M - Manganese ore
        commodity: "High-grade Mn ore",
        company: "South32 → JFE Mineral",
        flow_type: "manganese_ore"
    },
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 68.1,
        from_lon: -162.8,
        to_lat: 38.728,
        to_lon: 140.39,
        trade_value: 40000000, // $40M - Zinc ore
        commodity: "Sphalerite concentrate",
        company: "Teck Resources → JFE Mineral",
        flow_type: "zinc_ore"
    },
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 42.983,
        from_lon: 141.05,
        to_lat: 43.107,
        to_lon: -75.252,
        trade_value: 200000000, // $200M - Indium ore (rare/valuable)
        commodity: "Indium-bearing Sulfide Ore",
        company: "Dowa Holdings → Indium Corporation",
        flow_type: "indium_ore"
    },
    {
        from_country: "Russia",
        to_country: "Japan",
        from_lat: 69.4,
        from_lon: 88.1,
        to_lat: 33.25,
        to_lon: 131.7,
        trade_value: 150000000, // $150M - Nickel matte
        commodity: "High-Ni matte",
        company: "Nornickel → JX Metals",
        flow_type: "nickel_matte"
    },
    {
        from_country: "Russia",
        to_country: "Russia",
        from_lat: 69.4,
        from_lon: 88.1,
        to_lat: 69.4,
        to_lon: 88.1,
        trade_value: 80000000, // $80M - Nickel ore processing
        commodity: "Pentlandite ore",
        company: "Nornickel (mining to processing)",
        flow_type: "nickel_ore"
    },
    {
        from_country: "Canada",
        to_country: "Canada",
        from_lat: 46.493,
        from_lon: -80.995,
        to_lat: 46.493,
        to_lon: -80.995,
        trade_value: 60000000, // $60M - Nickel ore processing
        commodity: "Sulfide ore concentrate",
        company: "Glencore (mining to processing)",
        flow_type: "nickel_ore"
    },

    // Precious Metals
    {
        from_country: "USA",
        to_country: "USA",
        from_lat: 40.968,
        from_lon: -116.367,
        to_lat: 40.968,
        to_lon: -116.367,
        trade_value: 300000000, // $300M - Gold ore processing
        commodity: "Refractory Au ore",
        company: "Barrick Gold (mining to processing)",
        flow_type: "gold_ore"
    },
    {
        from_country: "Peru",
        to_country: "Peru",
        from_lat: -14.61,
        from_lon: -70.368,
        to_lat: -15.843,
        to_lon: -69.995,
        trade_value: 180000000, // $180M - Tin ore processing
        commodity: "Cassiterite concentrate",
        company: "Minsur (mining to processing)",
        flow_type: "tin_ore"
    },

    // Specialty Materials
    {
        from_country: "Japan",
        to_country: "Japan",
        from_lat: 37.916,
        from_lon: 139.04,
        to_lat: 35.999,
        to_lon: 136.188,
        trade_value: 120000000, // $120M - Barium titanate
        commodity: "BaTiO₃ ultrafine powder",
        company: "Nippon Chemical Industrial → Murata",
        flow_type: "ceramic_powder"
    },
    {
        from_country: "USA",
        to_country: "Japan",
        from_lat: 40.7,
        from_lon: -116,
        to_lat: 37.916,
        to_lon: 139.04,
        trade_value: 70000000, // $70M - Barite ore
        commodity: "Baryte (BaSO₄) ore",
        company: "Excalibar Minerals → Nippon Chemical",
        flow_type: "barite_ore"
    },
    {
        from_country: "Australia",
        to_country: "Japan",
        from_lat: -28.78,
        from_lon: 114.63,
        to_lat: 37.916,
        to_lon: 139.04,
        trade_value: 60000000, // $60M - Rutile mineral
        commodity: "TiO₂-rich rutile",
        company: "Iluka Resources → Nippon Chemical",
        flow_type: "rutile_mineral"
    },

    // Petroleum-Based Materials
    {
        from_country: "Saudi Arabia",
        to_country: "China",
        from_lat: 27.039,
        from_lon: 49.646,
        to_lat: 31.303,
        to_lon: 120.587,
        trade_value: 200000000, // $200M - BPA monomer
        commodity: "BPA monomer",
        company: "SABIC → Sumitomo Bakelite",
        flow_type: "chemical_monomer"
    },
    {
        from_country: "Saudi Arabia",
        to_country: "Saudi Arabia",
        from_lat: 25.19,
        from_lon: 49.24,
        to_lat: 27.039,
        to_lon: 49.646,
        trade_value: 150000000, // $150M - Crude oil processing
        commodity: "Sweet crude oil",
        company: "Saudi Aramco (extraction to processing)",
        flow_type: "crude_oil"
    },
    {
        from_country: "USA",
        to_country: "USA",
        from_lat: 29.735,
        from_lon: -94.957,
        to_lat: 28.96,
        to_lon: -95.36,
        trade_value: 100000000, // $100M - Propylene feedstock
        commodity: "Polymer-grade propylene",
        company: "ExxonMobil → Dow Chemical",
        flow_type: "petrochemical"
    },
    {
        from_country: "USA",
        to_country: "USA",
        from_lat: 31.9,
        from_lon: -102.1,
        to_lat: 29.735,
        to_lon: -94.957,
        trade_value: 80000000, // $80M - Texas crude
        commodity: "West Texas Light Sweet",
        company: "Pioneer Natural Resources → ExxonMobil",
        flow_type: "crude_oil"
    },

    // Glass Material Flows
    {
        from_country: "USA",
        to_country: "USA",
        from_lat: 33.561,
        from_lon: -81.721,
        to_lat: 33.561,
        to_lon: -81.721,
        trade_value: 45000000, // $45M - Glass processing
        commodity: "Glass melt slurry",
        company: "Owens Corning (internal processing)",
        flow_type: "glass_processing"
    },

    // Epoxy Resin System Flows
    {
        from_country: "China",
        to_country: "China",
        from_lat: 31.303,
        from_lon: 120.587,
        to_lat: 31.303,
        to_lon: 120.587,
        trade_value: 80000000, // $80M - Epoxy resin processing
        commodity: "Diglycidyl Ether of BPA (DGEBA)",
        company: "Sumitomo Bakelite (internal processing)",
        flow_type: "epoxy_processing"
    }
];

// Summary Statistics
const FLOW_SUMMARY = {
    total_flows: H100_SUPPLY_CHAIN_FLOWS.length,
    total_trade_value: H100_SUPPLY_CHAIN_FLOWS.reduce((sum, flow) => sum + flow.trade_value, 0),
    countries_involved: [...new Set(H100_SUPPLY_CHAIN_FLOWS.flatMap(flow => [flow.from_country, flow.to_country]))].length,
    flow_types: [...new Set(H100_SUPPLY_CHAIN_FLOWS.map(flow => flow.flow_type))],
    tier_breakdown: {
        tier_0_to_final: H100_SUPPLY_CHAIN_FLOWS.filter(f => f.to_country === "Global").length,
        tier_1_flows: H100_SUPPLY_CHAIN_FLOWS.filter(f => f.flow_type.includes("core_silicon") || f.flow_type.includes("memory") || f.flow_type.includes("packaging")).length,
        tier_2_flows: H100_SUPPLY_CHAIN_FLOWS.filter(f => f.flow_type.includes("power_") || f.flow_type.includes("passive_")).length,
        raw_materials: H100_SUPPLY_CHAIN_FLOWS.filter(f => f.flow_type.includes("ore") || f.flow_type.includes("crude")).length
    }
};

console.log('H100 Supply Chain Analysis:', FLOW_SUMMARY);
console.log(`Total Trade Value: $${(FLOW_SUMMARY.total_trade_value / 1e9).toFixed(1)}B`);
console.log(`Countries Involved: ${FLOW_SUMMARY.countries_involved}`);
console.log(`Total Flows Mapped: ${FLOW_SUMMARY.total_flows}`);

// Export for use in globe visualization
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { H100_SUPPLY_CHAIN_FLOWS, FLOW_SUMMARY };
}