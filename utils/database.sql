CREATE TABLE competitions (
        competition_id INTEGER PRIMARY KEY,
        competition_name TEXT,
        embed_info TEXT
    );
INSERT INTO competitions (competition_id, competition_name, embed_info) VALUES (123, '123', 'competition info from db');
CREATE TABLE scrambles (
        scramble_id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        event_id TEXT,
        round_type TEXT,
        scramble_num INTEGER,
        scramble TEXT,
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id)
    );
CREATE TABLE events (
        event_id TEXT PRIMARY KEY,
        event_name TEXT,
        format TEXT,
        average_id TEXT,
        FOREIGN KEY (average_id) REFERENCES formats(average_id)
    );
INSERT INTO events (event_id, event_name, format, average_id) VALUES ('333', '3x3 Cube', 'time', 'a');
INSERT INTO events (event_id, event_name, format, average_id) VALUES ('222', '2x2 Cube', 'time', 'a');
CREATE TABLE formats (
        average_id TEXT PRIMARY KEY,
        average_name TEXT,
        sort_by TEXT,
        sort_by_second TEXT,
        solve_count INTEGER,
        trim_fastest_n INTEGER,
        trim_slowest_n INTEGER
    );
INSERT INTO formats (average_id, average_name, sort_by, sort_by_second, solve_count, trim_fastest_n, trim_slowest_n) VALUES ('a', 'Average of 5', 'average', 'single', 5, 1, 1);
CREATE TABLE results (
        result_id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        event_id TEXT,
        user_id INTEGER,
        guild_id INTEGER,
        average_id TEXT,
        round_type_id TEXT,
        pos INTEGER,
        average INTEGER,
        value_1 INTERGER,
        value_2 INTEGER,
        value_3 INTEGER,
        value_4 INTEGER,
        value_5 INTEGER,
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id),
        FOREIGN KEY (average_id) REFERENCES formats(average_id)
    );
INSERT INTO results (result_id, competition_id, event_id, user_id, guild_id, average_id, round_type_id, pos, average, value_1, value_2, value_3, value_4, value_5) VALUES (1, 123, '333', 760616986568163348, 988085977719402536, 'a', '1', 1, 1234, 1234, 1234, 1234, 1234, 1234);
CREATE TABLE threads (
        thread_id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        event_id TEXT,
        user_id INTEGER,
        round_type TEXT,
        solve_num INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(event_id),
        FOREIGN KEY (competition_id) REFERENCES competitions(competition_id)
    );
INSERT INTO threads (thread_id, competition_id, event_id, user_id, round_type, solve_num) VALUES (1132792521890738217, 'competitionId', '333', 760616986568163348, '1', 1);
