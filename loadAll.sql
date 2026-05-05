USE CarCompanyDB;

INSERT INTO Role (role_id, role_name) VALUES
(1, 'Administrator'),
(2, 'Sales Staff'),
(3, 'Service Staff'),
(4, 'Finance Staff'),
(5, 'Accountant');

INSERT INTO Division (division_id, name) VALUES
(1, 'Sales'),
(2, 'Maintenance Services'),
(3, 'Financial Services');

INSERT INTO Department (department_id, name, division_id, active) VALUES
(1, 'Dealers New Car Sales', 1, TRUE),
(2, 'Dealers Used Car Sales', 1, TRUE),
(3, 'Online Used Car Sales', 1, TRUE),
(4, 'Maintenance Services', 2, TRUE),
(5, 'Financial Services and Loans', 3, TRUE),
(6, 'Accounting', 3, TRUE);

-- Passwords (werkzeug pbkdf2:sha256): admin=admin123, sales=sales123, service=service123, finance=finance123, accounting=accounting123
INSERT INTO `User` (user_id, username, password, name, address, email, department_id, role_id, active) VALUES
(1,  'admin',        'pbkdf2:sha256:1000000$QluBypzW$c8878a4973b88064553d1dcf45969c505c87f284e14507c08aa9ccde0aa22619', 'Alex Morgan',      '100 Corporate Plaza',      'alex.morgan@metroauto.com',     6, 1, TRUE),
(2,  'sales',        'pbkdf2:sha256:1000000$sHAbhF68$694b9c547c64cf7647d2e824f8c10db851ec6f1b716de0770946cb36ff5edba8', 'Samantha Reed',    '210 Dealer Row',           'samantha.reed@metroauto.com',   1, 2, TRUE),
(3,  'sales_used',   'pbkdf2:sha256:1000000$sHAbhF68$694b9c547c64cf7647d2e824f8c10db851ec6f1b716de0770946cb36ff5edba8', 'Taylor Brooks',    '215 Dealer Row',           'taylor.brooks@metroauto.com',   2, 2, TRUE),
(4,  'sales_online', 'pbkdf2:sha256:1000000$sHAbhF68$694b9c547c64cf7647d2e824f8c10db851ec6f1b716de0770946cb36ff5edba8', 'Olivia Chen',      '88 Digital Drive',         'olivia.chen@metroauto.com',     3, 2, TRUE),
(5,  'service',      'pbkdf2:sha256:1000000$wuR2fyN5$b0a5067444255bbc27a9dcf04afa683ad37e42a5d40d89c3bbff2fd54e5369dc', 'Jordan Patel',     '44 Service Road',          'jordan.patel@metroauto.com',    4, 3, TRUE),
(6,  'service_tech', 'pbkdf2:sha256:1000000$wuR2fyN5$b0a5067444255bbc27a9dcf04afa683ad37e42a5d40d89c3bbff2fd54e5369dc', 'Maria Gonzalez',   '46 Service Road',          'maria.gonzalez@metroauto.com',  4, 3, TRUE),
(7,  'finance',      'pbkdf2:sha256:1000000$sma5iI3L$3f6421c3902649fb106a66ee9a5f6e8d9ed68f08dbed8103e18cb8751ed45fe8', 'Casey Williams',   '500 Finance Avenue',       'casey.williams@metroauto.com',  5, 4, TRUE),
(8,  'loan_officer', 'pbkdf2:sha256:1000000$sma5iI3L$3f6421c3902649fb106a66ee9a5f6e8d9ed68f08dbed8103e18cb8751ed45fe8', 'Priya Nair',       '505 Finance Avenue',       'priya.nair@metroauto.com',      5, 4, TRUE),
(9,  'accounting',   'pbkdf2:sha256:1000000$qjZM73go$63d7bf3a41c915e63ae92de608f9528b546677fc7f676f12289688662d467644', 'Morgan Harris',    '700 Ledger Lane',          'morgan.harris@metroauto.com',   6, 5, TRUE),
(10, 'controller',   'pbkdf2:sha256:1000000$qjZM73go$63d7bf3a41c915e63ae92de608f9528b546677fc7f676f12289688662d467644', 'Daniel Kim',       '705 Ledger Lane',          'daniel.kim@metroauto.com',      6, 5, TRUE);

-- 10 customers
INSERT INTO Customer (customer_id, name, address, email) VALUES
(1,  'Emma Johnson',       '142 Maple Street',      'emma.johnson@example.com'),
(2,  'Liam Carter',        '87 Oak Avenue',         'liam.carter@example.com'),
(3,  'Sophia Martinez',    '530 Pine Road',         'sophia.martinez@example.com'),
(4,  'Noah Thompson',      '214 Cedar Lane',        'noah.thompson@example.com'),
(5,  'Ava Wilson',         '765 Birch Boulevard',   'ava.wilson@example.com'),
(6,  'Ethan Davis',        '319 Walnut Way',        'ethan.davis@example.com'),
(7,  'Mia Anderson',       '908 Spruce Street',     'mia.anderson@example.com'),
(8,  'Lucas Robinson',     '41 Elm Court',          'lucas.robinson@example.com'),
(9,  'Isabella Clark',     '672 Ash Drive',         'isabella.clark@example.com'),
(10, 'Benjamin Lewis',     '1200 Highland Avenue',  'benjamin.lewis@example.com');

-- 11 phone records (multi-value attribute test)
INSERT INTO CustomerPhone (customer_id, phone) VALUES
(1,  '2015550101'),
(1,  '2015550102'),
(2,  '2025550110'),
(3,  '2035550120'),
(4,  '2045550130'),
(5,  '2055550140'),
(6,  '2065550150'),
(7,  '2075550160'),
(8,  '2085550170'),
(9,  '2095550180'),
(10, '2105550190');

-- 13 vehicles: 10 sold (supports 10 sales), 3 available for demos
INSERT INTO Vehicle (vehicle_id, make, model, year, vin, price, mileage, condition_type, status) VALUES
(1,  'Ford',       'F-150',         2024, 'VIN10000000000001', 42000.00,  12,    'New',  'Sold'),
(2,  'Toyota',     'Camry',         2021, 'VIN10000000000002', 23500.00,  36000, 'Used', 'Sold'),
(3,  'Honda',      'Civic',         2022, 'VIN10000000000003', 21900.00,  28000, 'Used', 'Sold'),
(4,  'Chevrolet',  'Malibu',        2020, 'VIN10000000000004', 17500.00,  52000, 'Used', 'Sold'),
(5,  'Tesla',      'Model 3',       2023, 'VIN10000000000005', 38900.00,  9000,  'Used', 'Sold'),
(6,  'Nissan',     'Rogue',         2024, 'VIN10000000000006', 31000.00,  15,    'New',  'Sold'),
(7,  'Hyundai',    'Elantra',       2022, 'VIN10000000000007', 19900.00,  22000, 'Used', 'Sold'),
(8,  'BMW',        '3 Series',      2022, 'VIN10000000000008', 37000.00,  22000, 'Used', 'Available'),
(9,  'Ford',       'Mustang',       2023, 'VIN10000000000009', 32500.00,  9000,  'Used', 'Available'),
(10, 'Toyota',     'Highlander',    2024, 'VIN10000000000010', 41000.00,  300,   'New',  'Available'),
(11, 'Mercedes',   'C-Class',       2022, 'VIN10000000000011', 45000.00,  18000, 'Used', 'Sold'),
(12, 'Jeep',       'Grand Cherokee',2021, 'VIN10000000000012', 26500.00,  35000, 'Used', 'Sold'),
(13, 'Audi',       'A4',            2023, 'VIN10000000000013', 42000.00,  12000, 'Used', 'Sold');

-- 10 sales across all three sales departments
INSERT INTO Sales (sale_id, customer_id, vehicle_id, user_id, department_id, sale_price, sale_date, payment_method, financing_option) VALUES
(1,  1,  1,  2, 1, 41500.00, '2026-04-10', 'Financing',   TRUE),
(2,  2,  2,  3, 2, 22800.00, '2026-04-15', 'Cash',        FALSE),
(3,  3,  7,  4, 3, 19500.00, '2026-04-20', 'Credit Card', FALSE),
(4,  4,  3,  3, 2, 21500.00, '2026-04-25', 'Check',       FALSE),
(5,  5,  4,  4, 3, 16800.00, '2026-04-26', 'Credit Card', FALSE),
(6,  6,  5,  4, 3, 37900.00, '2026-04-27', 'Financing',   TRUE),
(7,  7,  6,  2, 1, 29500.00, '2026-04-28', 'Cash',   FALSE),
(8,  8,  11, 3, 2, 44000.00, '2026-04-29', 'Financing',   TRUE),
(9,  9,  12, 4, 3, 25500.00, '2026-04-30', 'Bank Transfer', FALSE),
(10, 10, 13, 2, 1, 41000.00, '2026-05-01', 'Credit Card', FALSE);

-- 10 service records
INSERT INTO Service (service_id, customer_id, vehicle_id, user_id, service_type, service_date, cost) VALUES
(1,  1,  1,  5, 'Oil Change',             '2026-04-22',  89.99),
(2,  2,  2,  6, 'Brake Inspection',       '2026-04-23', 149.99),
(3,  3,  7,  5, 'Tire Rotation',          '2026-04-24',  69.99),
(4,  4,  3,  6, 'Wheel Alignment',        '2026-04-25',  99.99),
(5,  5,  4,  5, 'Engine Tune-Up',         '2026-04-26', 189.99),
(6,  6,  5,  6, 'AC Recharge',            '2026-04-27', 129.99),
(7,  7,  6,  5, 'Transmission Flush',     '2026-04-28', 249.99),
(8,  8,  8,  6, 'Multi-Point Inspection', '2026-04-29',  79.99),
(9,  9,  9,  5, 'Battery Replacement',    '2026-04-30', 159.99),
(10, 10, 10, 6, 'Coolant Flush',          '2026-05-01', 109.99);

-- 10 parts-used records
INSERT INTO ServiceParts (service_id, part_name, part_cost) VALUES
(1,  'Oil Filter',          12.99),
(1,  'Engine Oil',          34.99),
(2,  'Brake Pads',          79.99),
(3,  'Tire Valve Caps',      4.99),
(4,  'Alignment Shims',     15.99),
(5,  'Spark Plugs',         24.99),
(5,  'Air Filter',          19.99),
(6,  'AC Refrigerant',      44.99),
(7,  'Transmission Fluid',  38.99),
(8,  'Engine Oil',          34.99);

-- 10 loans (tests Approved/Pending/Rejected statuses)
INSERT INTO Loan (loan_id, customer_id, vehicle_id, amount, interest_rate, term, monthly_payment, approval_status) VALUES
(1,  1,  1,  30000.00, 5.25, 60, 569.00, 'Approved'),
(2,  4,  5,  25000.00, 6.10, 48, 587.00, 'Pending'),
(3,  5,  6,  28000.00, 5.75, 60, 538.00, 'Approved'),
(4,  2,  2,  18000.00, 5.50, 48, 412.00, 'Approved'),
(5,  3,  7,  15000.00, 6.00, 36, 456.00, 'Approved'),
(6,  6,  11, 38000.00, 5.75, 60, 726.00, 'Approved'),
(7,  7,  12, 21000.00, 5.50, 48, 481.00, 'Pending'),
(8,  8,  13, 35000.00, 6.25, 72, 582.00, 'Approved'),
(9,  9,  8,  30000.00, 5.00, 60, 566.00, 'Approved'),
(10, 10, 9,  25000.00, 6.00, 48, 588.00, 'Rejected');

-- 10 loan payment records — tests balance tracking and payment history
INSERT INTO LoanPayment (loan_id, payment_date, amount, payment_method, remaining_balance) VALUES
(1,  '2026-05-01', 569.00, 'Bank Transfer', 29431.00),
(3,  '2026-05-02', 538.00, 'Credit Card',   27462.00),
(2,  '2026-05-03', 587.00, 'Check',         24413.00),
(4,  '2026-05-03', 412.00, 'Cash',          17588.00),
(5,  '2026-05-04', 456.00, 'Bank Transfer', 14544.00),
(6,  '2026-05-04', 726.00, 'Credit Card',   37274.00),
(8,  '2026-05-04', 582.00, 'Check',         34418.00),
(9,  '2026-05-05', 566.00, 'Bank Transfer', 29434.00),
(1,  '2026-05-05', 569.00, 'Credit Card',   28862.00),
(3,  '2026-05-05', 538.00, 'Cash',          26924.00);

-- 31 accounting entries covering sales, service, loan payments, and operational costs
INSERT INTO Accounting (type, amount, transaction_date, department_id) VALUES
('Sales',            41500.00, '2026-04-10', 1),
('Sales',            22800.00, '2026-04-15', 2),
('Sales',            19500.00, '2026-04-20', 3),
('Sales',            21500.00, '2026-04-25', 2),
('Sales',            16800.00, '2026-04-26', 3),
('Sales',            37900.00, '2026-04-27', 3),
('Sales',            29500.00, '2026-04-28', 1),
('Sales',            44000.00, '2026-04-29', 2),
('Sales',            25500.00, '2026-04-30', 3),
('Sales',            41000.00, '2026-05-01', 1),
('Service',             89.99, '2026-04-22', 4),
('Service',            149.99, '2026-04-23', 4),
('Service',             69.99, '2026-04-24', 4),
('Service',             99.99, '2026-04-25', 4),
('Service',            189.99, '2026-04-26', 4),
('Service',            129.99, '2026-04-27', 4),
('Service',            249.99, '2026-04-28', 4),
('Service',             79.99, '2026-04-29', 4),
('Service',            159.99, '2026-04-30', 4),
('Service',            109.99, '2026-05-01', 4),
('Loan',               569.00, '2026-05-01', 5),
('Loan',               538.00, '2026-05-02', 5),
('Loan',               587.00, '2026-05-03', 5),
('Loan',               412.00, '2026-05-03', 5),
('Loan',               456.00, '2026-05-04', 5),
('Loan',               726.00, '2026-05-04', 5),
('Loan',               582.00, '2026-05-04', 5),
('Loan',               566.00, '2026-05-05', 5),
('Loan',               569.00, '2026-05-05', 5),
('Loan',               538.00, '2026-05-05', 5),
('Expense',           1200.00, '2026-05-03', 6);
