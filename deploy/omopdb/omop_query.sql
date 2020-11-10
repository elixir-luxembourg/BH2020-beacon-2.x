select distinct on (p.person_id)
	p.person_id as subject_id,
	c_sex.concept_name as sex,
	'NCBITaxon:9606' as taxon_id,
	c_eth.concept_name as ethnicity,
	loc.county as geographic_origin,
	dis.diseases AS diseases,
	med.medications as medications,
	c_rac.concept_name as race
from "5_3_1".person as p inner join "5_3_1".condition_occurrence as c on p.person_id = c.person_id
	inner join "5_3_1".concept as c_sex on p.gender_concept_id = c_sex.concept_id
	inner join "5_3_1".concept as c_eth on p.ethnicity_concept_id = c_eth.concept_id
	/*inner join "5_3_1".concept as c_dis on c.condition_concept_id = c_dis.concept_id*/
	inner join "5_3_1".concept as c_rac on p.race_concept_id = c_rac.concept_id
	inner join "5_3_1".location as loc on p.location_id = loc.location_id
	left join lateral (
		select
			d.person_id,
			array_agg(concept_name) as diseases
		from "5_3_1".condition_occurrence d join "5_3_1".concept c on d.condition_concept_id = c.concept_id
		where person_id = p.person_id
		group by d.person_id
	) as dis ON TRUE
	left join lateral (
		select
			d.person_id,
			array_agg(concept_name) as medications
		from "5_3_1".drug_exposure d join "5_3_1".concept c on d.drug_concept_id = c.concept_id
		where person_id = p.person_id
		group by d.person_id
	) as med ON TRUE
limit 10;