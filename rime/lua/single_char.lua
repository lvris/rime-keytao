--[[
single_char_filter: 候选项重排序，使短注释/单字优先
--]]

local function single_char_filter(input)
    local l = {}
    for cand in input:iter() do
        if cand.comment and cand.comment:len() == 0 then
            yield(cand)
        else
            if (utf8.len(cand.text) == 1) then
                yield(cand)
            else
                table.insert(l, cand)
            end
        end
    end
    for i, cand in ipairs(l) do
        yield(cand)
    end
end

return single_char_filter
