-- report.game_statistics
select
    --[monthly] strftime('%Y-%m', collection_daily) as 集計月,
    --[yearly] strftime('%Y', collection_daily) as 集計年,
    count() / 4 as 対戦数,
    replace(printf('%.1fpt', round(sum(point), 1)), '-', '▲') as 供託,
    count(rpoint < -1 or null) as '飛んだ人数(延べ)',
    printf('%.2f%',	round(cast(count(rpoint < -1 or null) as real) / cast(count() / 4 as real) * 100, 2)) as トビ終了率,
    replace(printf('%s', max(rpoint)), '-', '▲') as 最大素点,
    replace(printf('%s', min(rpoint)), '-', '▲') as 最小素点
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
    --[individual] --[guest_not_skip] and game_info.guest_count <= 1 -- ゲストアリ(2ゲスト戦除外)
    --[individual] --[guest_skip] and results.guest = 0 -- ゲストナシ
group by
    --[monthly] strftime('%Y-%m', collection_daily)
    --[yearly] strftime('%Y', collection_daily)
order by
    --[monthly] strftime('%Y-%m', collection_daily) desc
    --[yearly] strftime('%Y', collection_daily) desc
;
