-- Config table
CREATE TABLE IF NOT EXISTS settings (
  module TEXT NOT NULL,
  entry TEXT NOT NULL,
  value_json TEXT NOT NULL,
  PRIMARY KEY(module, entry)
);

-- Text commands
CREATE TABLE IF NOT EXISTS commands (
  command TEXT PRIMARY KEY,
  response TEXT
);

-- URLs
CREATE TABLE IF NOT EXISTS urls (
  url TEXT PRIMARY KEY,
  redirect TEXT NOT NULL,
  comment TEXT,
  featured BOOLEAN DEFAULT FALSE
);
