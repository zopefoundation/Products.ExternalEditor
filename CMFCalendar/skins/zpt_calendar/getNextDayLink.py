##parameters=base_url, thisDay

# Takes a base url and returns a link to the previous day

thisDay += 1

x = '%s?date=%s' % (
                    base_url,
                    thisDay.Date()
                    )

return x