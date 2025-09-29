CREATE TABLE IF NOT EXISTS KYC(
    kyc_id TEXT PRIMARY KEY,
    document_number TEXT,
    verification_status TEXT DEFAULT 'Pending', --Pending, Completed
    verified_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Farmers(
    farmer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,      --prolly city mentioned here
    contact_number TEXT,
    kyc_id TEXT NOT NULL,
    joining_date DATE DEFAULT CURRENT_DATE,
    selling_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (kyc_id) REFERENCES KYC(kyc_id)
);

CREATE TABLE IF NOT EXISTS Consumers(
    consumer_id TEXT PRIMARY KEY,
    consumer_name TEXT,
    verification TEXT
    --rating and order will get referenced from their table
);

CREATE TABLE IF NOT EXISTS Aggregators(
    aggregator_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    contact_number TEXT,
    kyc_id TEXT,
    FOREIGN KEY (kyc_id) REFERENCES KYC(kyc_id)
);

CREATE TABLE IF NOT EXISTS Manufacturer(
    manufacturer_id TEXT PRIMARY KEY,
    manufacturer_name TEXT NOT NULL,
    kyc_id TEXT,
    FOREIGN KEY (kyc_id) REFERENCES KYC(kyc_id)
);

CREATE TABLE IF NOT EXISTS Batch(
    batch_id TEXT PRIMARY KEY,
    type TEXT,
    geotag TEXT,
    farmer_id TEXT,
    verification TEXT,
    aggregator_id TEXT,
    consumer_id TEXT,
    manufacturer_id TEXT,
    status TEXT DEFAULT 'Created',-- Created, Verified, Sold
    date DATE,
    time TIME,
    FOREIGN KEY (farmer_id) REFERENCES Farmers(farmer_id),
    FOREIGN KEY (aggregator_id) REFERENCES Aggregators(aggregator_id),
    FOREIGN KEY (consumer_id) REFERENCES Consumers(consumer_id),
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturer(manufacturer_id)
);

CREATE TABLE IF NOT EXISTS Inspection(
    inspector_id TEXT PRIMARY KEY,
    inspector_name TEXT,
    kyc_id TEXT,
    verification TEXT,
    batch_id TEXT,
    timestamp_verification TEXT,
    FOREIGN KEY (kyc_id) REFERENCES KYC(kyc_id),
    FOREIGN KEY (batch_id) REFERENCES Batch(batch_id)
);

CREATE TABLE IF NOT EXISTS Orders(
    order_id TEXT PRIMARY KEY,
    order_from TEXT,
    from_id TEXT,
    reciever TEXT,
    reciever_id TEXT,
    batch_id TEXT,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    status TEXT DEFAULT 'Pending',        -- Pending, Shipped, Completed, Cancelled
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES Batch(batch_id)
);

CREATE TABLE IF NOT EXISTS Ratings(
    rating_id TEXT PRIMARY KEY,
    consumer_id TEXT,
    farmer_id TEXT,
    rating REAL CHECK(rating >= 0 AND rating <= 5),
    FOREIGN KEY (consumer_id) REFERENCES Consumers(consumer_id),
    FOREIGN KEY (farmer_id) REFERENCES Farmers(farmer_id)
);
