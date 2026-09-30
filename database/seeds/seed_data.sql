USE stress_welfare_db;

-- Seed Users (passwords are bcrypt of shown values)
-- Admin@123, Welfare@123, Cmd@123, Med@123, Pers@123

INSERT INTO users (email, password_hash, full_name, role, unit_id) VALUES
('admin@crpf.gov.in',     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJbekRgQBpyA8PN4c1L2gFAK', 'System Administrator', 'super_admin', NULL),
('welfare@crpf.gov.in',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJbekRgQBpyA8PN4c1L2gFAK', 'Inspector Rajesh Kumar', 'welfare_officer', 1),
('commander@crpf.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJbekRgQBpyA8PN4c1L2gFAK', 'DIG Amit Singh', 'commander', 1),
('medical@crpf.gov.in',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMlJbekRgQBpyA8PN4c1L2gFAK', 'Dr. Priya Sharma', 'medical_officer', 1);

-- Seed Personnel (names/service_numbers will be encrypted by app; using placeholder text here)
INSERT INTO personnel (anon_id, service_number, name, unit_id, unit_name, rank, years_of_service, deployment_zone, family_station, date_of_joining, current_posting_date) VALUES
(UUID(), 'PLACEHOLDER_ENC', 'PLACEHOLDER_ENC', 1, '139 Bn CRPF', 'Constable', 8, 'field', FALSE, '2016-03-15', '2023-01-10'),
(UUID(), 'PLACEHOLDER_ENC', 'PLACEHOLDER_ENC', 1, '139 Bn CRPF', 'Head Constable', 12, 'high_altitude', FALSE, '2012-07-20', '2022-06-01'),
(UUID(), 'PLACEHOLDER_ENC', 'PLACEHOLDER_ENC', 2, '88 Bn CRPF', 'Constable', 5, 'counter_terror', FALSE, '2019-01-05', '2024-02-15'),
(UUID(), 'PLACEHOLDER_ENC', 'PLACEHOLDER_ENC', 2, '88 Bn CRPF', 'ASI', 15, 'peace', TRUE, '2009-08-10', '2023-09-01'),
(UUID(), 'PLACEHOLDER_ENC', 'PLACEHOLDER_ENC', 1, '139 Bn CRPF', 'Constable', 3, 'insurgency', FALSE, '2021-04-12', '2024-04-12');

-- Seed Leave Records
INSERT INTO leave_records (personnel_id, leave_type, start_date, end_date, days, status) VALUES
(1, 'annual', '2024-12-01', '2024-12-10', 10, 'approved'),
(1, 'casual', '2025-02-14', '2025-02-15', 2, 'denied'),
(2, 'annual', '2025-01-05', '2025-01-20', 15, 'approved'),
(3, 'emergency', '2025-03-10', '2025-03-12', 3, 'approved'),
(5, 'annual', '2025-01-15', '2025-01-30', 15, 'denied');

-- Seed Deployment Records
INSERT INTO deployment_records (personnel_id, location, zone, start_date, is_current) VALUES
(1, 'Baramulla, J&K', 'field', '2023-01-10', TRUE),
(2, 'Siachen Region', 'high_altitude', '2022-06-01', TRUE),
(3, 'Chhattisgarh', 'counter_terror', '2024-02-15', TRUE),
(4, 'Delhi HQ', 'peace', '2023-09-01', TRUE),
(5, 'Manipur', 'insurgency', '2024-04-12', TRUE);
