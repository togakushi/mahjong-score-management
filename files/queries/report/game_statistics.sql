-- report.game_statistics
select
    --[not_collection] strftime('%Y-%m', collection_daily) as 集計月,
    --[monthly] strftime('%Y-%m', collection_daily) as 集計月,
    --[yearly] strftime('%Y', collection_daily) as 集計年,
    --[collection_all] '全体' as 集計,
    count() / 4 as 対戦数,
    round(sum(point), 1) + 0 as deposit,
    count(rpoint < -1 or null) as '飛んだ人数(延べ)',
    round(cast(count(rpoint < -1 or null) as real) / cast(count() / 4 as real) * 100, 2) as トビ終了率,
    max(rpoint) * 100 as rpoint_max,
    min(rpoint) * 100 as rpoint_min
from
    individual_results as results
join game_info on
    game_info.ts = results.ts
where
    game_info.mode = :mode
    and game_info.rule_version in (<<rule_list>>)
    and game_info.playtime between :starttime and :endtime
    --[separate] and game_info.source = :source
    --[search_word] and game_info.comment like :search_word
    --[guest_not_skip] and game_info.guest_count <= 1 -- ゲストアリ(2ゲスト戦除外)
group by
    --[not_collection] strftime('%Y-%m', collection_daily)
    --[monthly] strftime('%Y-%m', collection_daily)
    --[yearly] strftime('%Y', collection_daily)
    --[collection_all] '集計'
order by
    --[not_collection] strftime('%Y-%m', collection_daily) desc
    --[monthly] strftime('%Y-%m', collection_daily) desc
    --[yearly] strftime('%Y', collection_daily) desc
    --[collection_all] '集計'
;
