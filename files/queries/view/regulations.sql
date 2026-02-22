
create view if not exists regulations as
    select
        remarks.thread_ts,
        remarks.name as name,
        ifnull(team.name, '未所属') as team,
        case when member.id isnull then 1 else 0 end as guest,
        group_concat(remarks.matter) as word,
        count() as count,
        ifnull(words.type, rule.undefined_word) as type,
        sum(ifnull(words.ex_point, 0)) as ex_point,
        rule.rule_version
    from
        remarks
    join result on
        result.ts = remarks.thread_ts
    join rule on
        rule.rule_version = result.rule_version
    left join member on
        member.name = remarks.name
    left join team on
        member.team_id = team.id
    left join words on
        words.word = remarks.matter
        and words.rule_version = result.rule_version
    group by
        remarks.thread_ts, remarks.name, words.type
;
