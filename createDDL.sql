DROP DATABASE IF EXISTS CarCompanyDB;
CREATE DATABASE CarCompanyDB;
USE CarCompanyDB;

CREATE TABLE Role (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Division (
    division_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    division_id INT,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (division_id) REFERENCES Division(division_id)
);

CREATE TABLE `User` (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    address TEXT,
    email VARCHAR(100) UNIQUE,
    department_id INT,
    role_id INT,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (role_id) REFERENCES Role(role_id),
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
);

CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    email VARCHAR(100)
);

CREATE TABLE CustomerPhone (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    phone VARCHAR(10),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Vehicle (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    make VARCHAR(50),
    model VARCHAR(50),
    year INT,
    vin VARCHAR(50) UNIQUE NOT NULL,
    price DECIMAL(10,2),
    mileage INT,
    condition_type VARCHAR(20),
    status VARCHAR(20)
);

CREATE TABLE Sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    user_id INT,
    department_id INT,
    sale_price DECIMAL(10,2),
    sale_date DATE,
    payment_method VARCHAR(50),
    financing_option BOOLEAN,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (user_id) REFERENCES `User`(user_id),
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
);

CREATE TABLE Service (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    user_id INT,
    service_type VARCHAR(100),
    service_date DATE,
    cost DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id),
    FOREIGN KEY (user_id) REFERENCES `User`(user_id)
);

CREATE TABLE ServiceParts (
    part_id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT,
    part_name VARCHAR(100),
    part_cost DECIMAL(10,2),
    FOREIGN KEY (service_id) REFERENCES Service(service_id)
);

CREATE TABLE Loan (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    vehicle_id INT,
    amount DECIMAL(10,2),
    interest_rate DECIMAL(5,2),
    term INT,
    monthly_payment DECIMAL(10,2),
    approval_status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicle(vehicle_id)
);

CREATE TABLE LoanPayment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    payment_date DATE,
    amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    remaining_balance DECIMAL(10,2),
    FOREIGN KEY (loan_id) REFERENCES Loan(loan_id)
);

CREATE TABLE Accounting (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    amount DECIMAL(10,2),
    transaction_date DATE,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
);
