INSERT INTO events (event_id, event_name, format, average_id) VALUES ('pyram', 'Pyraminx', 'time', 'a');
INSERT INTO events (event_id, event_name, format, average_id) VALUES ('skewb', 'Skewb', 'time', 'a');

INSERT INTO competitions (competition_id, competition_name) VALUES ('UtcWeekOneAug', 'Unravelling The Cube week one');

INSERT INTO competition_events (competition_id, event_id) VALUES ('UtcWeekOneAug', '222');
INSERT INTO competition_events (competition_id, event_id) VALUES ('UtcWeekOneAug', '333');
INSERT INTO competition_events (competition_id, event_id) VALUES ('UtcWeekOneAug', 'pyram');
INSERT INTO competition_events (competition_id, event_id) VALUES ('UtcWeekOneAug', 'skewb');

INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '333', 'f', 1, 'B2 D2 B F'' L2 B U2 L2 U2 L'' B'' U2 F'' D'' F'' L'' F'' U R');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '333', 'f', 2, 'D'' L'' D R U R'' D'' U2 B U2 R2 F2 R2 F R2 U2 F L2 B'' L U');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '333', 'f', 3, 'F R L D2 L2 U F B2 R'' B2 L'' B2 R'' B2 R2 U2 L F U''');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '333', 'f', 4, 'B'' R2 B2 D B R2 U'' R'' F B D2 B D2 R2 U2 B2 D2 L2 B'' L');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '333', 'f', 5, 'U2 B2 D2 L2 D2 F D2 B U2 L2 B'' D2 R'' U B'' F2 D2 B'' U'' R');

INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '222', 'f', 1, 'R2 U2 F'' U2 F U'' F2 R'' U2');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '222', 'f', 2, 'R2 F R U2 F'' R F'' U R');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '222', 'f', 3, 'R U'' F2 U F'' R F R'' F''');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '222', 'f', 4, 'F2 R'' F'' U2 R F'' R U R'' U2');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', '222', 'f', 5, 'U R F'' R2 F2 U R'' U F''');

INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'pyram', 'f', 1, 'R B'' U'' B L'' R U L r b u');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'pyram', 'f', 2, 'R L'' R U L'' U R'' U r b u''');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'pyram', 'f', 3, 'L U'' L'' U'' B R'' B'' L'' r b'' u');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'pyram', 'f', 4, 'U L'' B L'' B'' R'' L U'' b u''');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'pyram', 'f', 5, 'L'' R U'' R B U B'' L l r''');

INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'skewb', 'f', 1, 'R L R'' B'' R'' U L'' U');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'skewb', 'f', 2, 'U'' R L B U'' R'' U L''');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'skewb', 'f', 3, 'U B'' U B'' R B'' R'' L R B');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'skewb', 'f', 4, 'U'' B R B U L'' R U'' R''');
INSERT INTO scrambles (competition_id, event_id, round_type, scramble_num, scramble) VALUES ('UtcWeekOneAug', 'skewb', 'f', 5, 'L'' U L'' U B L'' U L'' B');





