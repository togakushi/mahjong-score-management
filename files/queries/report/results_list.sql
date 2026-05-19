-- report.results_list
with target_data as (
    select
        --[individual] --[unregistered_replace] case when results.guest = 0 then results.name else :guest_name end as name, -- ゲスト有効
        --[individual] --[unregistered_not_replace] case when results.guest = 0 then results.name else results.name || '(<<guest_mark>>)' end as name, -- ゲスト無効
        --[team] results.team as name,
        --[individual] point,
        --[team] team_point as point,
        rpoint,
        rank,
        count as yakuman_count
    from
        individual_results as results
    join game_info on
        game_info.ts = results.ts
    left join regulations on
        regulations.thread_ts = results.ts
        and regulations.name = results.name
        and regulations.type = 0
    where
        results.mode = :mode
        and results.rule_version in (<<rule_list>>)
        and results.playtime between :starttime and :endtime
        --[separate] and results.source = :source
        --[individual] --[guest_not_skip] and game_info.guest_count <= 1 -- ゲストアリ(2ゲスト戦除外)
        --[individual] --[guest_skip] and results.guest = 0 -- ゲストナシ
        --[individual] --[player_name] and results.name in (<<player_list>>) -- 対象プレイヤー
        --[team] --[friendly_fire] and game_info.same_team = 0
        --[team] and results.team != '未所属' -- 未所属除外
        --[team] --[player_name] and results.team in (<<player_list>>) -- 対象チーム
        --[search_word] and game_info.comment like :search_word
    order by
        results.playtime desc
    --[recent] limit :target_count * 4 -- 直近N(縦持ちなので4倍する)
),
summary_data as (
    select
        name,
        count() as "game",
        round(sum(point), 1) as "total_point",
        round(avg(point), 1) as "avg_point",
        count(rank = 1 or null) as "rank1_count",
        cast(count(rank = 1 or null) as real) / count() as "rank1_rate",
        count(rank = 1.5 or null) as "rank1.5_count",
        cast(count(rank = 1.5 or null) as real) / count() as "rank1.5_rate",
        count(rank = 2 or null) as "rank2_count",
        cast(count(rank = 2 or null) as real) / count() as "rank2_rate",
        count(rank = 2.5 or null) as "rank2.5_count",
        cast(count(rank = 2.5 or null) as real) / count() as "rank2.5_rate",
        count(rank = 3 or null) as "rank3_count",
        cast(count(rank = 3 or null) as real) / count() as "rank3_rate",
        count(rank = 3.5 or null) as "rank3.5_count",
        cast(count(rank = 3.5 or null) as real) / count() as "rank3.5_rate",
        count(rank = 4 or null) as "rank4_count",
        cast(count(rank = 4 or null) as real) / count() as "rank4_rate",
        avg(rank) as "rank_avg",
        count(rpoint < 0 or null) as "flying_count",
        cast(count(rpoint < 0 or null) as real) / count() as "flying_rate",
        ifnull(sum(yakuman_count), 0) as "yakuman_count",
        cast(ifnull(sum(yakuman_count), 0) as real) / count() as "yakuman_rate"
    from
        target_data
    group by
        name
    having
        count() >= :stipulated -- 規定打数
    order by
        sum(point) desc
)
select
    printf("%6.2f%% (%3d)", "rank1_rate" * 100, "rank1_count" ) as "rank1_rate-count",
    printf("%6.2f%% (%3d)", "rank1.5_rate" * 100, "rank1.5_count") as "rank1.5_rate-count",
    printf("%6.2f%% (%3d)", "rank2_rate" * 100, "rank2_count" ) as "rank2_rate-count",
    printf("%6.2f%% (%3d)", "rank2.5_rate" * 100, "rank2.5_count") as "rank2.5_rate-count",
    printf("%6.2f%% (%3d)", "rank3_rate" * 100, "rank3_count" ) as "rank3_rate-count",
    printf("%6.2f%% (%3d)", "rank3.5_rate" * 100, "rank3.5_count") as "rank3.5_rate-count",
    printf("%6.2f%% (%3d)", "rank4_rate" * 100, "rank4_count" ) as "rank4_rate-count",
    printf("%6.2f%% (%3d)", "flying_rate" * 100, "flying_count" ) as "flying_rate-count",
    printf("%6.2f%% (%3d)", "yakuman_rate" * 100, "yakuman_count") as "yakuman_rate-count",
    *
from
    summary_data
;
