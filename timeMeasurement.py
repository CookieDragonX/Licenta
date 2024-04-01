import time

def measure_time_with_mean(fct):
    exec_times_dict = {}
    # fnc_name -> [nr_exec, [list of exec times]]
    def inner(*argv, **kwargs):
        t0=time.time()
        rez=fct(*argv, **kwargs)
        t1=time.time()
        if(fct.__name__ not in exec_times_dict):
            exec_times_dict[fct.__name__] = [1,[t1-t0]]
        else:
            exec_times_dict[fct.__name__][0]+=1
            exec_times_dict[fct.__name__][1].append(t1-t0)
        print(f'Execution time is : {t1-t0} for function {fct.__name__}')
        print(f'This is execution number : {exec_times_dict[fct.__name__][0]}')
        print(f'Medium exec time: {sum(exec_times_dict[fct.__name__][1])/exec_times_dict[fct.__name__][0]}')
        return rez
    return inner

def measure_time(fct):
    def inner(*argv, **kwargs):
        t0=time.time()
        rez=fct(*argv, **kwargs)
        t1=time.time()
        print(f'Execution time is : {t1-t0} for function {fct.__name__}')
        return rez
    return inner