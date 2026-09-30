CREATE DATABASE IF NOT EXISTS stress_welfare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stress_welfare_db;

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(150) NOT NULL,
  role ENUM('super_admin','welfare_officer','commander','medical_officer','personnel') NOT NULL,
  unit_id INT NULL,
  personnel_id INT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_login DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_email (email), INDEX idx_role (role)
);

-- 2. PERSONNEL
CREATE TABLE IF NOT EXISTS personnel (
  id INT AUTO_INCREMENT PRIMARY KEY,
  anon_id VARCHAR(64) UNIQUE NOT NULL,
  service_number BLOB NOT NULL,
  name BLOB NOT NULL,
  unit_id INT NULL,
  unit_name VARCHAR(100) NULL,
  rank VARCHAR(50) NULL,
  years_of_service INT DEFAULT 0,
  deployment_zone ENUM('peace','field','high_altitude','insurgency','counter_terror') DEFAULT 'peace',
  family_station BOOLEAN DEFAULT FALSE,
  date_of_joining DATE NULL,
  current_posting_date DATE NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_unit (unit_id), INDEX idx_zone (deployment_zone)
);

-- 3. LEAVE RECORDS
CREATE TABLE IF NOT EXISTS leave_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  leave_type ENUM('annual','casual','medical','emergency','special') NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  days INT NOT NULL,
  status ENUM('approved','pending','denied','cancelled') DEFAULT 'pending',
  reason TEXT NULL,
  applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  INDEX idx_personnel_leave (personnel_id), INDEX idx_status (status)
);

-- 4. DEPLOYMENT RECORDS
CREATE TABLE IF NOT EXISTS deployment_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  location VARCHAR(200) NOT NULL,
  zone ENUM('peace','field','high_altitude','insurgency','counter_terror') DEFAULT 'peace',
  start_date DATE NOT NULL,
  end_date DATE NULL,
  duration_days INT NULL,
  is_current BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  INDEX idx_personnel_dep (personnel_id), INDEX idx_current (is_current)
);

-- 5. DUTY SCHEDULES
CREATE TABLE IF NOT EXISTS duty_schedules (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  week_start DATE NOT NULL,
  duty_hours FLOAT DEFAULT 0,
  overtime_hours FLOAT DEFAULT 0,
  night_shifts INT DEFAULT 0,
  total_shifts INT DEFAULT 0,
  consecutive_duty_days INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  INDEX idx_personnel_duty (personnel_id)
);

-- 6. WELLNESS ASSESSMENTS
CREATE TABLE IF NOT EXISTS wellness_assessments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  score FLOAT NOT NULL,
  mood_score INT NULL,
  sleep_quality INT NULL,
  energy_level INT NULL,
  stress_level INT NULL,
  social_support INT NULL,
  responses JSON NULL,
  consent_given BOOLEAN DEFAULT FALSE,
  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  INDEX idx_personnel_wellness (personnel_id)
);

-- 7. RISK SCORES
CREATE TABLE IF NOT EXISTS risk_scores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  score_date DATE NOT NULL,
  stress_score DECIMAL(5,2) DEFAULT 0.00,
  burnout_score DECIMAL(5,2) DEFAULT 0.00,
  overall_risk ENUM('LOW','MODERATE','HIGH','CRITICAL') DEFAULT 'LOW',
  risk_factors JSON NULL,
  model_version VARCHAR(20) DEFAULT 'v1.0',
  is_anomaly BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  INDEX idx_personnel_risk (personnel_id, score_date),
  INDEX idx_risk_level (overall_risk)
);

-- 8. ALERTS
CREATE TABLE IF NOT EXISTS alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  alert_type ENUM('HIGH_STRESS','BURNOUT','ANOMALY','SELF_REPORT','MANUAL') NOT NULL,
  severity ENUM('LOW','MEDIUM','HIGH','URGENT') NOT NULL,
  status ENUM('OPEN','ACKNOWLEDGED','RESOLVED','ESCALATED') DEFAULT 'OPEN',
  assigned_to INT NULL,
  notes TEXT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  acknowledged_at DATETIME NULL,
  resolved_at DATETIME NULL,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
  INDEX idx_status (status), INDEX idx_severity (severity), INDEX idx_created (created_at)
);

-- 9. INTERVENTIONS
CREATE TABLE IF NOT EXISTS interventions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  personnel_id INT NOT NULL,
  alert_id INT NULL,
  officer_id INT NOT NULL,
  intervention_type ENUM('counseling','leave_approved','workload_reduced','medical_referral','family_support','other') NOT NULL,
  description TEXT NULL,
  outcome TEXT NULL,
  follow_up_date DATE NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (personnel_id) REFERENCES personnel(id) ON DELETE CASCADE,
  FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE SET NULL,
  FOREIGN KEY (officer_id) REFERENCES users(id)
);

-- 10. AUDIT LOGS (immutable)
CREATE TABLE IF NOT EXISTS audit_logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  action VARCHAR(100) NOT NULL,
  target_table VARCHAR(50) NULL,
  target_id INT NULL,
  ip_address VARCHAR(45) NULL,
  user_agent TEXT NULL,
  extra_data JSON NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_ts (user_id, timestamp), INDEX idx_action (action)
);

-- 11. RAG CONVERSATIONS
CREATE TABLE IF NOT EXISTS rag_conversations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  session_id VARCHAR(64) NOT NULL,
  use_case ENUM('CHATBOT','RECOMMENDATION','CASE_SEARCH','EXPLANATION','COMPANION') NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  source_docs JSON NULL,
  model_used VARCHAR(50) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_session (user_id, session_id)
);
