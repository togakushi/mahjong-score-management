-- team.info.sql
select
    team.id,
    team.name as team,
    group_concat(member.name) as members
from
    team
left join member on
    member.team_id = team.id
group by
    team.name
order by
    team.id
;
