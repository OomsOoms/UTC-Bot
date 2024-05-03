CREATE TABLE IF NOT EXISTS "competitions" (
	"competition_id"	TEXT,
	"competition_name"	TEXT,
	"host_id"	INTEGER,
	"active"	INTEGER,
	"extra_info"	TEXT,
	PRIMARY KEY("competition_id")
);
CREATE TABLE IF NOT EXISTS "competition_events" (
	"competition_id"	TEXT,
	"event_id"	TEXT,
	"video_evidence"	INTEGER,
	FOREIGN KEY("event_id") REFERENCES "events"("event_id"),
	FOREIGN KEY("competition_id") REFERENCES "competitions"("competition_id")
);
CREATE TABLE IF NOT EXISTS "scrambles" (
	"competition_id"	INTEGER,
	"event_id"	TEXT,
	"round_type"	TEXT,
	"scramble_num"	INTEGER,
	"scramble"	TEXT,
	FOREIGN KEY("event_id") REFERENCES "events"("event_id"),
	FOREIGN KEY("competition_id") REFERENCES "competitions"("competition_id"),
	PRIMARY KEY("competition_id","event_id","round_type","scramble_num")
);
CREATE TABLE IF NOT EXISTS "events" (
	"event_id"	TEXT,
	"event_name"	TEXT,
	"format"	TEXT,
	"average_id"	TEXT,
	FOREIGN KEY("average_id") REFERENCES "formats"("average_id"),
	PRIMARY KEY("event_id")
);
CREATE TABLE IF NOT EXISTS "formats" (
	"average_id"	TEXT,
	"average_name"	TEXT,
	"solve_count"	INTEGER,
	"trim_n"	INTEGER,
	PRIMARY KEY("average_id")
);
CREATE TABLE IF NOT EXISTS "threads" (
	"thread_id"	INTEGER,
	"competition_id"	INTEGER,
	"event_id"	TEXT,
	"user_id"	INTEGER,
	"round_type"	TEXT,
	"solve_num"	INTEGER,
	"value_1"	INTEGER,
	"value_2"	INTEGER,
	"value_3"	INTEGER,
	"value_4"	INTEGER,
	"value_5"	INTEGER,
	FOREIGN KEY("competition_id") REFERENCES "competitions"("competition_id"),
	FOREIGN KEY("event_id") REFERENCES "events"("event_id"),
	PRIMARY KEY("thread_id")
);
CREATE TABLE IF NOT EXISTS "results" (
	"result_id"	INTEGER,
	"competition_id"	INTEGER,
	"event_id"	TEXT,
	"user_id"	INTEGER,
	"guild_id"	INTEGER,
	"round_type"	TEXT,
	"average"	INTEGER,
	"value_1"	INTEGER,
	"value_2"	INTEGER,
	"value_3"	INTEGER,
	"value_4"	INTEGER,
	"value_5"	INTEGER,
	"video_link"	TEXT,
	PRIMARY KEY("result_id"),
	FOREIGN KEY("competition_id") REFERENCES "competitions"("competition_id"),
	FOREIGN KEY("event_id") REFERENCES "events"("event_id")
);
