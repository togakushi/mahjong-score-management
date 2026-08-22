-- summary.consecutive
with rolling_tbl as (
    select
        --[individual] --[unregistered_replace] case when results.guest = 0 then results.name else :guest_name end as name, -- ゲスト有効
        --[individual] --[unregistered_not_replace] case when results.guest = 0 then results.name else results.name || '(<<guest_mark>>)' end as name, -- ゲスト無効
        --[team] results.team as name,
        results.playtime as end_time,
        first_value(results.playtime) over(
            partition by name
            order by results.playtime asc
            rows between :chain - 1 preceding and current row
        ) as start_time,
        row_number() over (
            partition by name
            order by results.playtime asc
        ) as match_num,
        sum(point) over (
            partition by name
            order by results.playtime asc
            rows between :chain - 1 preceding and current row
        ) as rolling_point,
        group_concat(round(point, 1), ' ') over (
            partition by name
            order by results.playtime asc
            rows between :chain - 1 preceding and current row
        ) as consecutive_record,
        group_concat(rank, ' ') over (
            partition by name
            order by results.playtime asc
            rows between :chain - 1 preceding and current row
        ) as acquisition_rank,
		count(rpoint < 0 or NULL) over (
            partition by name
            order by results.playtime asc
            rows between :chain - 1 preceding and current row
        ) as flying_count
    from
        individual_results as results
    join game_info
        on game_info.ts = results.ts
    where
        results.mode = :mode and seat <= :mode
        and results.rule_version in (<<rule_list>>)
        and results.playtime between :starttime and :endtime
        --[separate] and results.source = :source
        --[individual] --[guest_not_skip] and game_info.guest_count <= 1 -- ゲストアリ(2ゲスト戦除外)
        --[individual] --[guest_skip] and results.guest = 0 -- ゲストナシ
        --[individual] --[player_name] and results.name in (<<player_list>>) -- 対象プレイヤー
        --[team] and results.team != '未所属' -- 未所属除外
        --[team] --[friendly_fire] and game_info.same_team = 0
        --[team] --[player_name] and results.team in (<<player_list>>) -- 対象チーム
        --[search_word] and game_info.comment like :search_word
),
matches_tbl as (
    select
        name,
        start_time,
        end_time,
        rolling_point,
		consecutive_record,
		acquisition_rank,
		flying_count,
        max(match_num) over (
            partition by name
        ) as total_game,
        row_number() over (
            partition by name
            order by rolling_point desc, end_time asc
        ) as score_rank
    from
        rolling_tbl
    where
        match_num >= :chain
)
select
    name,
    round(rolling_point, 1) as rolling_point,
	consecutive_record,
	acquisition_rank,
	flying_count,
    start_time,
    end_time,
    total_game
from
    matches_tbl
where
	score_rank >= :chain
order by
    --[ascending] rolling_point asc,
    --[descending] rolling_point desc,
    start_time asc
limit :ranked
;
