from .create_competition import Competition
import pickle



deserialized_object = pickle.loads(b'\x80\x04\x95\xe8\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main__\x94\x8c\x0bCompetition\x94\x93\x94)\x81\x94}\x94(\x8c\x10competition_name\x94\x8c\x0cfuckyouerrir\x94\x8c\x0bcompetitors\x94]\x94\x8c\x08settings\x94}\x94(\x8c\nhost_users\x94]\x94\x8c\x0cround_length\x94K\x00\x8c\x0clive_results\x94\x89\x8c\x0evideo_evidence\x94\x89\x8c\nstart_date\x94K\x00\x8c\x06guilds\x94]\x94u\x8c\x0ecompetition_id\x94\x8c\x13Fuckyouerrir0623013\x94ub.')
print(deserialized_object)