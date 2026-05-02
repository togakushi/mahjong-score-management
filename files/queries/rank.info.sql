-- rank.info
with target_data as (
    select
        playtime,
        seat,
        --[individual] --[unregistered_replace] case when guest = 0 then name else :guest_name end as name, -- ゲスト有効
        --[individual] --[unregistered_not_replace] case when guest = 0 then name else name || '(<<guest_mark>>)' end as name, -- ゲスト無効
        --[team] team as name,
        rpoint,
        --[individual] point,
        --[team] team_point as point,
        rank,
        rpoint - origin_point as score,
        yakuman,
        comment
    from (
        select
            *,
            sum(guest) over (partition by playtime) as guest_count,
            count() over (partition by playtime, team) as same_team
        from
            individual_results
        join rule
            on
                individual_results.rule_version = rule.rule_version
    )
    where
        mode = :mode and seat <= :mode
        and rule_version in (<<rule_list>>)
        and playtime between :starttime and :endtime
        --[separate] and source = :source
        --[individual] --[guest_not_skip] and guest_count <= 1 -- ゲストアリ(2ゲスト戦除外)
        --[individual] --[guest_skip] and guest = 0 -- ゲストナシ
        --[individual] --[player_name] and name in (<<player_list>>) -- 対象プレイヤー
        --[team] and team != '未所属' -- 未所属除外
        --[team] --[friendly_fire] and same_team != 0
        --[team] --[player_name] and team in (<<player_list>>) -- 対象チーム
        --[search_word] and comment like :search_word
)
select distinct
    playtime,
    name,
    case
        when id = 1 then '東家'
        when id = 2 then '南家'
        when id = 3 then '西家'
        when id = 4 then '北家'
        else '全体'
    end as seat,
    id,
    rank
from (
    select
        seat as id, *
    from
        target_data
    union all select
        0 as id, *
    from
        target_data
)
order by
    name, id
;
