select p.person_id as subject_id,
	co.concept_name as sex,
	'NCBITaxon:9606' as taxon_id,
	c_eth.concept_name as ethnicity,
	loc.county as geographic_origin,
	c_con.concept_name as disease,
	c_rac.concept_name as race
from "5_3_1".person as p, "5_3_1".condition_occurrence as c,
	"5_3_1".concept as co,
	"5_3_1".concept as c_eth,
	"5_3_1".concept as c_con,	
	"5_3_1".concept as c_rac,	
	"5_3_1".location as loc
	where p.person_id = c.person_id and
		p.gender_concept_id = co.concept_id and
		p.ethnicity_concept_id = c_eth.concept_id and
		p.location_id = loc.location_id and
		c.condition_concept_id = c_con.concept_id and
		p.race_concept_id = c_rac.concept_id
limit 10;