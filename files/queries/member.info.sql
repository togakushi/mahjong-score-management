-- member.info.sql
with member_status as (
    select
    name,
    max(playtime) as last_update,
    (strftime('%s', datetime('now', 'localtime')) - strftime('%s', max(playtime))) / 60 / 60 / 24 as elapsed_day,
    count() as game_count
from
    individual_results
where
    mode = :mode
    and rule_version in (<<rule_list>>)
    and guest = 0
group by
    name
),
alias_list as (
select
    name,
    group_concat(name) as alias_list
from
    alias
group by
    member
)
select
    member.id,
    member.name as name,
    alias_list as alias,
    ifnull(team.name, '未所属') as team,
    last_update,
    elapsed_day,
    game_count
from
    member
left join team on
    team.id = member.team_id
left join member_status on
    member_status.name = member.name
left join alias_list on
    alias_list.name = member.name
where
    member.id != 0
order by
    member.id
;
