def connect(start: tuple[int, int], end: tuple[int, int], steps=100):
    some_number = (start[0] + end[0]) // 2
    if end[0] < start[0]:
        print(f"{end} to {start} should have been another path")
        # return some kind of round path

    if start[1] == end[1]:
        return start, end

    points = [
        start,
        (some_number, start[1]),
        (some_number, end[1]),
        end]
    return bezier(points, steps)


def bezier(points: list[tuple[int, int]], steps: int) -> list[tuple[any, ...]]:
    combinations = [1., 3., 3., 1.]
    result = []
    for t in [t/steps for t in range(steps + 1)]:
        t_powers = (t**i for i in range(4))
        u_powers = reversed([(1-t)**i for i in range(4)])
        co_efs = [c*a*b for c, a, b in zip(combinations, t_powers, u_powers)]
        result.append(
            tuple(sum([co_ef*p for co_ef, p in zip(co_efs, ps)]) for ps in zip(*points)))

    return result
