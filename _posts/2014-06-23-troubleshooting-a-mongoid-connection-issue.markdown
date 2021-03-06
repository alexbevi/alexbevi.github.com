---
layout: post
title: "Troubleshooting a Mongoid Connection Issue"
date: 2014-06-23 10:27:58 -0400
comments: true
categories: [MongoDB]
tags: [mongodb, mongoid, rails, ruby]
---

I've been struggling with an issue for a while now regarding Mongoid connections just freezing when the host is not on *localhost*. I've tried posting this on [stack overflow](https://stackoverflow.com/questions/24210058/mongoid-4-mongodb-2-4-freezing-issue) and [GitHub](https://github.com/mongoid/moped/issues/274), but haven't really gotten anywhere.

I'm now trying to dive into the issue using GDB directly, which I'm starting off following the [NewRelic blog post](http://blog.newrelic.com/2013/04/29/debugging-stuck-ruby-processes-what-to-do-before-you-kill-9/) about debugging hung Ruby processes.

First, once the process is frozen, I connect using:

    sudo gdb -p <pid>

and then tried to get some info from the C-level backtraces via:

    (gdb) t a a bt

This resulted in a lot of information that didn't really help me (at least not immediately):

<!--more-->

```
Thread 8 (Thread 0x7f032a5e1700 (LWP 9001)):
#0  0x00007f0329c0ffbd in poll () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007f032a0d1d60 in timer_thread_sleep (gvl=0x1ed8f28) at thread_pthread.c:1381
#2  thread_timer (p=0x1ed8f28) at thread_pthread.c:1456
#3  0x00007f032990c182 in start_thread (arg=0x7f032a5e1700) at pthread_create.c:312
#4  0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 7 (Thread 0x7f032a4c0700 (LWP 9002)):
#0  sem_wait () at ../nptl/sysdeps/unix/sysv/linux/x86_64/sem_wait.S:85
#1  0x00007f032495b75d in v8::internal::LinuxSemaphore::Wait() ()
   from gems/ruby-2.1.1/extensions/x86_64-linux/2.1.0/therubyracer-0.12.1/v8/init.so
#2  0x00007f032486104c in v8::internal::RuntimeProfiler::WaitForSomeIsolateToEnterJS() ()
   from gems/ruby-2.1.1/extensions/x86_64-linux/2.1.0/therubyracer-0.12.1/v8/init.so
#3  0x00007f032495b968 in v8::internal::SignalSender::Run() ()
   from gems/ruby-2.1.1/extensions/x86_64-linux/2.1.0/therubyracer-0.12.1/v8/init.so
#4  0x00007f032495b86e in v8::internal::ThreadEntry(void*) ()
   from gems/ruby-2.1.1/extensions/x86_64-linux/2.1.0/therubyracer-0.12.1/v8/init.so
#5  0x00007f032990c182 in start_thread (arg=0x7f032a4c0700) at pthread_create.c:312
#6  0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 6 (Thread 0x7f0321988700 (LWP 9008)):
#0  0x00007f0329c14c33 in select () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007f032a0d8cdb in rb_fd_select (n=<optimized out>, readfds=<optimized out>, writefds=<optimized out>, exceptfds=<optimized out>,
    timeout=<optimized out>) at thread.c:3321
#2  0x00007f032a0d9139 in native_fd_select (th=<optimized out>, timeout=0x7f0321987550, exceptfds=0x0, writefds=0x0, readfds=0x7f0321987810,
    n=12) at thread_pthread.c:1007
#3  do_select (timeout=0x7f0321987550, except=0x0, write=0x0, read=0x7f0321987810, n=12) at thread.c:3436
#4  rb_thread_fd_select (max=max@entry=12, read=read@entry=0x7f0321987810, write=write@entry=0x0, except=except@entry=0x0,
    timeout=timeout@entry=0x7f03219877e0) at thread.c:3582
#5  0x00007f0329f96150 in select_internal (fds=0x7f0321987810, tp=0x7f03219877e0, except=<optimized out>, write=<optimized out>,
    read=<optimized out>) at io.c:8232
#6  select_call (arg=arg@entry=139651425269744) at io.c:8302
#7  0x00007f0329f67d97 in rb_ensure (b_proc=b_proc@entry=0x7f0329f95e30 <select_call>, data1=data1@entry=139651425269744,
    e_proc=e_proc@entry=0x7f0329f926a0 <select_end>, data2=data2@entry=139651425269744) at eval.c:850
#8  0x00007f0329f92810 in rb_f_select (argc=<optimized out>, argv=<optimized out>, obj=<optimized out>) at io.c:8651
#9  0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f0321a88f20, th=0x96c91c0) at vm_insnhelper.c:1470
#10 vm_call_cfunc (th=0x96c91c0, reg_cfp=0x7f0321a88f20, ci=<optimized out>) at vm_insnhelper.c:1560
#11 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x96c91c0, initial=initial@entry=0) at insns.def:1028
#12 0x00007f032a0bb5ec in vm_exec (th=0x96c91c0) at vm.c:1304
#13 0x00007f032a0be89f in vm_invoke_proc (th=th@entry=0x96c91c0, proc=0x96c9690, self=133280920, defined_class=117512440, argc=0,
    argv=0x7f1b228, blockptr=blockptr@entry=0x0) at vm.c:788
#14 0x00007f032a0be8da in rb_vm_invoke_proc (th=th@entry=0x96c91c0, proc=<optimized out>, argc=<optimized out>, argv=<optimized out>,
    blockptr=blockptr@entry=0x0) at vm.c:807
#15 0x00007f032a0d475d in thread_start_func_2 (th=th@entry=0x96c91c0, stack_start=<optimized out>) at thread.c:535
#16 0x00007f032a0d4a9b in thread_start_func_1 (th_ptr=0x96c91c0) at thread_pthread.c:803
#17 0x00007f032990c182 in start_thread (arg=0x7f0321988700) at pthread_create.c:312
#18 0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 5 (Thread 0x7f0321786700 (LWP 9009)):
#0  pthread_cond_timedwait@@GLIBC_2.3.2 () at ../nptl/sysdeps/unix/sysv/linux/x86_64/pthread_cond_timedwait.S:238
#1  0x00007f032a0d27ff in native_cond_timedwait (ts=<optimized out>, mutex=<optimized out>, cond=<optimized out>) at thread_pthread.c:352
#2  native_sleep (th=0x96c9870, timeout_tv=0x7f03217857c0) at thread_pthread.c:1061
#3  0x00007f032a0d55fa in sleep_timeval (th=0x96c9870, tv=..., spurious_check=spurious_check@entry=1) at thread.c:1046
#4  0x00007f032a0d57ba in rb_thread_wait_for (time=...) at thread.c:1115
#5  0x00007f0329ff27d0 in rb_f_sleep (argc=1, argv=0x7f0321787038) at process.c:4193
#6  0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f0321886f70, th=0x96c9870) at vm_insnhelper.c:1470
#7  vm_call_cfunc (th=0x96c9870, reg_cfp=0x7f0321886f70, ci=<optimized out>) at vm_insnhelper.c:1560
#8  0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x96c9870, initial=initial@entry=0) at insns.def:1028
#9  0x00007f032a0bb5ec in vm_exec (th=0x96c9870) at vm.c:1304
#10 0x00007f032a0be89f in vm_invoke_proc (th=th@entry=0x96c9870, proc=0x96c9d90, self=133279880, defined_class=117256360, argc=0,
    argv=0x7f1afd0, blockptr=blockptr@entry=0x0) at vm.c:788
#11 0x00007f032a0be8da in rb_vm_invoke_proc (th=th@entry=0x96c9870, proc=<optimized out>, argc=<optimized out>, argv=<optimized out>,
    blockptr=blockptr@entry=0x0) at vm.c:807
#12 0x00007f032a0d475d in thread_start_func_2 (th=th@entry=0x96c9870, stack_start=<optimized out>) at thread.c:535
#13 0x00007f032a0d4a9b in thread_start_func_1 (th_ptr=0x96c9870) at thread_pthread.c:803
#14 0x00007f032990c182 in start_thread (arg=0x7f0321786700) at pthread_create.c:312
#15 0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 4 (Thread 0x7f0321584700 (LWP 9010)):
#0  0x00007f0329c14c33 in select () at ../sysdeps/unix/syscall-template.S:81
#1  0x00007f032a0d8cdb in rb_fd_select (n=<optimized out>, readfds=<optimized out>, writefds=<optimized out>, exceptfds=<optimized out>,
    timeout=<optimized out>) at thread.c:3321
#2  0x00007f032a0d9139 in native_fd_select (th=<optimized out>, timeout=0x0, exceptfds=0x0, writefds=0x0, readfds=0x7f0321583810, n=11)
    at thread_pthread.c:1007
#3  do_select (timeout=0x0, except=0x0, write=0x0, read=0x7f0321583810, n=11) at thread.c:3436
#4  rb_thread_fd_select (max=max@entry=11, read=read@entry=0x7f0321583810, write=write@entry=0x0, except=except@entry=0x0,
    timeout=timeout@entry=0x0) at thread.c:3582
#5  0x00007f0329f96150 in select_internal (fds=0x7f0321583810, tp=0x0, except=<optimized out>, write=<optimized out>, read=<optimized out>)
    at io.c:8232
#6  select_call (arg=arg@entry=139651421059056) at io.c:8302
#7  0x00007f0329f67d97 in rb_ensure (b_proc=b_proc@entry=0x7f0329f95e30 <select_call>, data1=data1@entry=139651421059056,
    e_proc=e_proc@entry=0x7f0329f926a0 <select_end>, data2=data2@entry=139651421059056) at eval.c:850
#8  0x00007f0329f92810 in rb_f_select (argc=<optimized out>, argv=<optimized out>, obj=<optimized out>) at io.c:8651
#9  0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f0321684f20, th=0x96c9f10) at vm_insnhelper.c:1470
#10 vm_call_cfunc (th=0x96c9f10, reg_cfp=0x7f0321684f20, ci=<optimized out>) at vm_insnhelper.c:1560
#11 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x96c9f10, initial=initial@entry=0) at insns.def:1028
#12 0x00007f032a0bb5ec in vm_exec (th=0x96c9f10) at vm.c:1304
#13 0x00007f032a0be89f in vm_invoke_proc (th=th@entry=0x96c9f10, proc=0x96ec480, self=133126360, defined_class=118126960, argc=0,
    argv=0x7f1adf0, blockptr=blockptr@entry=0x0) at vm.c:788
#14 0x00007f032a0be8da in rb_vm_invoke_proc (th=th@entry=0x96c9f10, proc=<optimized out>, argc=<optimized out>, argv=<optimized out>,
    blockptr=blockptr@entry=0x0) at vm.c:807
#15 0x00007f032a0d475d in thread_start_func_2 (th=th@entry=0x96c9f10, stack_start=<optimized out>) at thread.c:535
#16 0x00007f032a0d4a9b in thread_start_func_1 (th_ptr=0x96c9f10) at thread_pthread.c:803
#17 0x00007f032990c182 in start_thread (arg=0x7f0321584700) at pthread_create.c:312
#18 0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 3 (Thread 0x7f0321180700 (LWP 9472)):
#0  0x00007f0329c1007f in __GI_ppoll (fds=fds@entry=0x7f032117bb90, nfds=nfds@entry=1, timeout=<optimized out>, timeout@entry=0x0,
    sigmask=sigmask@entry=0x0) at ../sysdeps/unix/sysv/linux/ppoll.c:56
#1  0x00007f032a0d9b28 in rb_wait_for_single_fd (fd=fd@entry=15, events=events@entry=1, tv=tv@entry=0x0) at thread.c:3656
#2  0x00007f032a0da044 in rb_thread_wait_fd_rw (read=1, fd=fd@entry=15) at thread.c:3495
#3  rb_thread_wait_fd (fd=fd@entry=15) at thread.c:3506
#4  0x00007f0329f9693f in rb_io_wait_readable (f=15) at io.c:1092
#5  0x00007f0329f97cee in io_bufread (ptr=0x7f03042c3440 "", len=36, fptr=0x7f0310054420) at io.c:2035
#6  0x00007f0329f97e24 in bufread_call (arg=arg@entry=139651416833616) at io.c:2071
#7  0x00007f0329f67d97 in rb_ensure (b_proc=b_proc@entry=0x7f0329f97e10 <bufread_call>, data1=data1@entry=139651416833616,
    e_proc=e_proc@entry=0x7f032a04f900 <rb_str_unlocktmp>, data2=<optimized out>) at eval.c:850
#8  0x00007f032a05e8db in rb_str_locktmp_ensure (str=<optimized out>, func=func@entry=0x7f0329f97e10 <bufread_call>,
    arg=arg@entry=139651416833616) at string.c:2004
#9  0x00007f0329f9ad06 in io_fread (fptr=0x7f0310054420, size=36, offset=0, str=139650673747040) at io.c:2085
#10 io_read (argc=<optimized out>, argv=<optimized out>, io=35833440) at io.c:2816
#11 0x00007f032a0bfae1 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127e770, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#12 vm_call_cfunc (ci=<optimized out>, reg_cfp=0x7f032127e770, th=0x7f030c0455c0) at vm_insnhelper.c:1560
---Type <return> to continue, or q <return> to quit---
#13 vm_call_method (th=0x7f030c0455c0, cfp=0x7f032127e770, ci=<optimized out>) at vm_insnhelper.c:1754
#14 0x00007f032a0b7b9c in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1050
#15 0x00007f032a0bb5ec in vm_exec (th=th@entry=0x7f030c0455c0) at vm.c:1304
#16 0x00007f032a0c2cff in invoke_block_from_c (defined_class=79426520, cref=0x0, blockptr=0x0, argv=0x7f032117c2e8, argc=1, self=72558880,
    block=<optimized out>, th=0x7f030c0455c0) at vm.c:732
#17 vm_yield (argv=<optimized out>, argc=<optimized out>, th=<optimized out>) at vm.c:763
#18 rb_yield_0 (argv=0x7f032117c2e8, argc=1) at vm_eval.c:938
#19 rb_yield (val=<optimized out>) at vm_eval.c:948
#20 0x00007f0329f1d4bd in rb_ary_collect (ary=139650673749800) at array.c:2684
#21 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127ea90, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#22 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f032127ea90, ci=<optimized out>) at vm_insnhelper.c:1560
#23 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:999
#24 0x00007f032a0bb5ec in vm_exec (th=th@entry=0x7f030c0455c0) at vm.c:1304
#25 0x00007f032a0c2cff in invoke_block_from_c (defined_class=80043920, cref=0x0, blockptr=0x0, argv=0x7f032117c6c8, argc=1,
    self=139650673695240, block=<optimized out>, th=0x7f030c0455c0) at vm.c:732
#26 vm_yield (argv=<optimized out>, argc=<optimized out>, th=<optimized out>) at vm.c:763
#27 rb_yield_0 (argv=0x7f032117c6c8, argc=1) at vm_eval.c:938
#28 rb_yield (val=<optimized out>) at vm_eval.c:948
#29 0x00007f0329f15fa2 in rb_ary_each (array=139650673713080) at array.c:1792
#30 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127f170, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#31 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f032127f170, ci=<optimized out>) at vm_insnhelper.c:1560
#32 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:999
#33 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#34 0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0455c0, proc=proc@entry=0x7f0304886b90, self=139650673713320, defined_class=78042600,
    argc=argc@entry=0, argv=argv@entry=0x7f0321182020, blockptr=0x0) at vm.c:788
#35 0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x7f0304886b90, argc=argc@entry=0,
    argv=argv@entry=0x7f0321182020, blockptr=<optimized out>) at vm.c:807
#36 0x00007f0329f6e550 in proc_call (argc=0, argv=0x7f0321182020, procval=139650673713160) at proc.c:734
#37 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127f300, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#38 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f032127f300, ci=<optimized out>) at vm_insnhelper.c:1560
#39 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1028
#40 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#41 0x00007f032a0be89f in vm_invoke_proc (th=th@entry=0x7f030c0455c0, proc=0x9676cb0, self=139650673658200, defined_class=79743600, argc=1,
    argv=argv@entry=0x7f032117d0a0, blockptr=0x0) at vm.c:788
#42 0x00007f032a0bea45 in vm_call_bmethod_body (argv=0x7f032117d0a0, ci=0x7f032117d280, th=0x7f030c0455c0) at vm_insnhelper.c:1592
#43 vm_call_bmethod (th=th@entry=0x7f030c0455c0, cfp=cfp@entry=0x7f032127f7b0, ci=ci@entry=0x7f032117d280) at vm_insnhelper.c:1607
#44 0x00007f032a0bfc1e in vm_call_method (th=th@entry=0x7f030c0455c0, cfp=cfp@entry=0x7f032127f7b0, ci=ci@entry=0x7f032117d280)
    at vm_insnhelper.c:1774
#45 0x00007f032a0bf691 in vm_call_opt_send (th=0x7f030c0455c0, reg_cfp=0x7f032127f7b0, ci=0x7f032117d280) at vm_insnhelper.c:1657
#46 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1028
#47 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#48 0x00007f032a0bec82 in vm_yield_with_cref (cref=<optimized out>, argv=<optimized out>, argc=<optimized out>, th=0x7f030c0455c0) at vm.c:755
#49 yield_under (under=<optimized out>, self=<optimized out>, values=139650673660760) at vm_eval.c:1531
#50 0x00007f032a0bfae1 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127f9e0, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#51 vm_call_cfunc (ci=<optimized out>, reg_cfp=0x7f032127f9e0, th=0x7f030c0455c0) at vm_insnhelper.c:1560
#52 vm_call_method (th=0x7f030c0455c0, cfp=0x7f032127f9e0, ci=<optimized out>) at vm_insnhelper.c:1754
#53 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:999
#54 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#55 0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0455c0, proc=proc@entry=0x7f030010a480, self=83224000, defined_class=87087200,
    argc=argc@entry=2, argv=argv@entry=0x7f0321181c90, blockptr=0x0) at vm.c:788
#56 0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x7f030010a480, argc=argc@entry=2,
    argv=argv@entry=0x7f0321181c90, blockptr=<optimized out>) at vm.c:807
#57 0x00007f0329f6e550 in proc_call (argc=2, argv=0x7f0321181c90, procval=139651130810120) at proc.c:734
#58 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127fa80, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#59 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f032127fa80, ci=<optimized out>) at vm_insnhelper.c:1560
#60 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1028
#61 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#62 0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0455c0, proc=proc@entry=0x7f030010a560, self=87087800, defined_class=87087760,
    argc=argc@entry=1, argv=argv@entry=0x7f0321181c38, blockptr=0x0) at vm.c:788
#63 0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x7f030010a560, argc=argc@entry=1,
    argv=argv@entry=0x7f0321181c38, blockptr=<optimized out>) at vm.c:807
#64 0x00007f0329f6e550 in proc_call (argc=1, argv=0x7f0321181c38, procval=139651130809960) at proc.c:734
#65 0x00007f032a0bfae1 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127fb20, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#66 vm_call_cfunc (ci=<optimized out>, reg_cfp=0x7f032127fb20, th=0x7f030c0455c0) at vm_insnhelper.c:1560
#67 vm_call_method (th=0x7f030c0455c0, cfp=0x7f032127fb20, ci=<optimized out>) at vm_insnhelper.c:1754
#68 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1028
#69 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#70 0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0455c0, proc=proc@entry=0x7f030010a720, self=87087800, defined_class=87087760,
    argc=argc@entry=1, argv=argv@entry=0x7f0321181be0, blockptr=0x0) at vm.c:788
#71 0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x7f030010a720, argc=argc@entry=1,
    argv=argv@entry=0x7f0321181be0, blockptr=<optimized out>) at vm.c:807
#72 0x00007f0329f6e550 in proc_call (argc=1, argv=0x7f0321181be0, procval=139651130809560) at proc.c:734
#73 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032127fbc0, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#74 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f032127fbc0, ci=<optimized out>) at vm_insnhelper.c:1560
#75 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1028
#76 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
---Type <return> to continue, or q <return> to quit---
#77 0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0455c0, proc=proc@entry=0x7f0304529c40, self=156831200, defined_class=50567600,
    argc=argc@entry=1, argv=argv@entry=0x7f0321181990, blockptr=0x0) at vm.c:788
#78 0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x7f0304529c40, argc=argc@entry=1,
    argv=argv@entry=0x7f0321181990, blockptr=<optimized out>) at vm.c:807
#79 0x00007f0329f6e550 in proc_call (argc=1, argv=0x7f0321181990, procval=139650673670240) at proc.c:734
#80 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f0321280070, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#81 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f0321280070, ci=<optimized out>) at vm_insnhelper.c:1560
#82 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:1028
#83 0x00007f032a0bb5ec in vm_exec (th=th@entry=0x7f030c0455c0) at vm.c:1304
#84 0x00007f032a0c2cff in invoke_block_from_c (defined_class=76547880, cref=0x0, blockptr=0x0, argv=0x7f032117ee08, argc=1, self=34415960,
    block=<optimized out>, th=0x7f030c0455c0) at vm.c:732
#85 vm_yield (argv=<optimized out>, argc=<optimized out>, th=<optimized out>) at vm.c:763
#86 rb_yield_0 (argv=0x7f032117ee08, argc=1) at vm_eval.c:938
#87 rb_yield (val=<optimized out>) at vm_eval.c:948
#88 0x00007f0329f15fa2 in rb_ary_each (array=139650673629520) at array.c:1792
#89 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f03212801b0, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#90 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f03212801b0, ci=<optimized out>) at vm_insnhelper.c:1560
#91 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:999
#92 0x00007f032a0bb5ec in vm_exec (th=th@entry=0x7f030c0455c0) at vm.c:1304
#93 0x00007f032a0c2924 in invoke_block_from_c (defined_class=80036240, cref=0x0, blockptr=0x0, argv=0x7f032117f1c8, argc=1, self=120753520,
    block=<optimized out>, th=0x7f030c0455c0) at vm.c:732
#94 vm_yield (argv=0x7f032117f1c8, argc=1, th=0x7f030c0455c0) at vm.c:763
#95 rb_yield_0 (argv=0x7f032117f1c8, argc=1) at vm_eval.c:938
#96 catch_i (tag=<optimized out>, data=data@entry=0) at vm_eval.c:1772
#97 0x00007f032a0b4b4a in rb_catch_protect (t=<optimized out>, func=func@entry=0x7f032a0c26c0 <catch_i>, data=data@entry=0,
    stateptr=stateptr@entry=0x7f032117f340) at vm_eval.c:1858
#98 0x00007f032a0b4bbc in rb_catch_obj (t=<optimized out>, func=func@entry=0x7f032a0c26c0 <catch_i>, data=data@entry=0) at vm_eval.c:1837
#99 0x00007f032a0b4c6e in rb_f_catch (argc=<optimized out>, argv=<optimized out>) at vm_eval.c:1823
#100 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f03212802f0, th=0x7f030c0455c0) at vm_insnhelper.c:1470
#101 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f03212802f0, ci=<optimized out>) at vm_insnhelper.c:1560
#102 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:999
#103 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#104 0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0455c0, proc=proc@entry=0x96c8680, self=133126360, defined_class=118126960,
    argc=argc@entry=2, argv=argv@entry=0x7f0321181070, blockptr=0x0) at vm.c:788
#105 0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x96c8680, argc=argc@entry=2,
    argv=argv@entry=0x7f0321181070, blockptr=<optimized out>) at vm.c:807
#106 0x00007f0329f6e550 in proc_call (argc=2, argv=0x7f0321181070, procval=133281320) at proc.c:734
#107 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f0321280f70, th=0x7f030c0455c0) at vm_insnhelper.c:1470
---Type <return> to continue, or q <return> to quit---
#108 vm_call_cfunc (th=0x7f030c0455c0, reg_cfp=0x7f0321280f70, ci=<optimized out>) at vm_insnhelper.c:1560
#109 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0455c0, initial=initial@entry=0) at insns.def:999
#110 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0455c0) at vm.c:1304
#111 0x00007f032a0be89f in vm_invoke_proc (th=th@entry=0x7f030c0455c0, proc=0x7f030c044ca0, self=133281640, defined_class=117256680, argc=0,
    argv=0x7f02f4c943a0, blockptr=blockptr@entry=0x0) at vm.c:788
#112 0x00007f032a0be8da in rb_vm_invoke_proc (th=th@entry=0x7f030c0455c0, proc=<optimized out>, argc=<optimized out>, argv=<optimized out>,
    blockptr=blockptr@entry=0x0) at vm.c:807
#113 0x00007f032a0d475d in thread_start_func_2 (th=th@entry=0x7f030c0455c0, stack_start=<optimized out>) at thread.c:535
#114 0x00007f032a0d4a9b in thread_start_func_1 (th_ptr=0x7f030c0455c0) at thread_pthread.c:803
#115 0x00007f032990c182 in start_thread (arg=0x7f0321180700) at pthread_create.c:312
#116 0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 2 (Thread 0x7f0320f7e700 (LWP 9563)):
#0  pthread_cond_wait@@GLIBC_2.3.2 () at ../nptl/sysdeps/unix/sysv/linux/x86_64/pthread_cond_wait.S:185
#1  0x00007f032a0d6ce3 in native_cond_wait (mutex=0x8ef42b0, cond=0x8ef42d8) at thread_pthread.c:334
#2  lock_func (timeout_ms=0, mutex=0x8ef42b0, th=0x7f030c0485d0) at thread.c:4324
#3  rb_mutex_lock (self=120765160) at thread.c:4398
#4  0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032107ebb0, th=0x7f030c0485d0) at vm_insnhelper.c:1470
#5  vm_call_cfunc (th=0x7f030c0485d0, reg_cfp=0x7f032107ebb0, ci=<optimized out>) at vm_insnhelper.c:1560
#6  0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x7f030c0485d0, initial=initial@entry=0) at insns.def:1028
#7  0x00007f032a0bb5ec in vm_exec (th=0x7f030c0485d0) at vm.c:1304
#8  0x00007f032a0be89f in vm_invoke_proc (th=0x7f030c0485d0, proc=proc@entry=0x96c8680, self=133126360, defined_class=118126960,
    argc=argc@entry=2, argv=argv@entry=0x7f0320f7f070, blockptr=0x0) at vm.c:788
#9  0x00007f032a0be8da in rb_vm_invoke_proc (th=<optimized out>, proc=proc@entry=0x96c8680, argc=argc@entry=2,
    argv=argv@entry=0x7f0320f7f070, blockptr=<optimized out>) at vm.c:807
#10 0x00007f0329f6e550 in proc_call (argc=2, argv=0x7f0320f7f070, procval=133281320) at proc.c:734
#11 0x00007f032a0b3024 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032107ef70, th=0x7f030c0485d0) at vm_insnhelper.c:1470
#12 vm_call_cfunc (th=0x7f030c0485d0, reg_cfp=0x7f032107ef70, ci=<optimized out>) at vm_insnhelper.c:1560
#13 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x7f030c0485d0, initial=initial@entry=0) at insns.def:999
#14 0x00007f032a0bb5ec in vm_exec (th=0x7f030c0485d0) at vm.c:1304
#15 0x00007f032a0be89f in vm_invoke_proc (th=th@entry=0x7f030c0485d0, proc=0x7f030c047b40, self=133281640, defined_class=117256680, argc=0,
    argv=0x7f02f4cd2290, blockptr=blockptr@entry=0x0) at vm.c:788
#16 0x00007f032a0be8da in rb_vm_invoke_proc (th=th@entry=0x7f030c0485d0, proc=<optimized out>, argc=<optimized out>, argv=<optimized out>,
    blockptr=blockptr@entry=0x0) at vm.c:807
#17 0x00007f032a0d475d in thread_start_func_2 (th=th@entry=0x7f030c0485d0, stack_start=<optimized out>) at thread.c:535
#18 0x00007f032a0d4a9b in thread_start_func_1 (th_ptr=0x7f030c0485d0) at thread_pthread.c:803
#19 0x00007f032990c182 in start_thread (arg=0x7f0320f7e700) at pthread_create.c:312
#20 0x00007f0329c1d30d in clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:111

Thread 1 (Thread 0x7f032a5c2740 (LWP 8999)):
#0  pthread_cond_wait@@GLIBC_2.3.2 () at ../nptl/sysdeps/unix/sysv/linux/x86_64/pthread_cond_wait.S:185
#1  0x00007f032a0d2390 in native_cond_wait (mutex=0x1ed96d0, cond=<optimized out>) at thread_pthread.c:334
#2  native_sleep (th=th@entry=0x1ed95b0, timeout_tv=0x0) at thread_pthread.c:1059
#3  0x00007f032a0d618a in sleep_forever (deadlockable=1, spurious_check=0, th=0x1ed95b0) at thread.c:996
#4  thread_join_sleep (arg=arg@entry=140734195440096) at thread.c:787
#5  0x00007f0329f67d97 in rb_ensure (b_proc=b_proc@entry=0x7f032a0d6090 <thread_join_sleep>, data1=data1@entry=140734195440096,
    e_proc=e_proc@entry=0x7f032a0cfa10 <remove_from_join_list>, data2=data2@entry=140734195440096) at eval.c:850
#6  0x00007f032a0d0cd0 in thread_join (delay=<optimized out>, target_th=0x96c9f10) at thread.c:829
#7  thread_join_m (argc=<optimized out>, argv=0x7f032a4c1168, self=<optimized out>) at thread.c:909
#8  0x00007f032a0bfae1 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032a5c0ca0, th=0x1ed95b0) at vm_insnhelper.c:1470
#9  vm_call_cfunc (ci=<optimized out>, reg_cfp=0x7f032a5c0ca0, th=0x1ed95b0) at vm_insnhelper.c:1560
#10 vm_call_method (th=0x1ed95b0, cfp=0x7f032a5c0ca0, ci=<optimized out>) at vm_insnhelper.c:1754
#11 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x1ed95b0, initial=initial@entry=0) at insns.def:1028
#12 0x00007f032a0bb5ec in vm_exec (th=th@entry=0x1ed95b0) at vm.c:1304
#13 0x00007f032a0c2cff in invoke_block_from_c (defined_class=51649880, cref=0x0, blockptr=0x0, argv=0x7fff3bba1e08, argc=1, self=51647880,
    block=<optimized out>, th=0x1ed95b0) at vm.c:732
#14 vm_yield (argv=<optimized out>, argc=<optimized out>, th=<optimized out>) at vm.c:763
#15 rb_yield_0 (argv=0x7fff3bba1e08, argc=1) at vm_eval.c:938
#16 rb_yield (val=val@entry=52428600) at vm_eval.c:948
#17 0x00007f0329fcb079 in rb_obj_tap (obj=52428600) at object.c:675
#18 0x00007f032a0bfae1 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032a5c0e30, th=0x1ed95b0) at vm_insnhelper.c:1470
#19 vm_call_cfunc (ci=<optimized out>, reg_cfp=0x7f032a5c0e30, th=0x1ed95b0) at vm_insnhelper.c:1560
#20 vm_call_method (th=0x1ed95b0, cfp=0x7f032a5c0e30, ci=<optimized out>) at vm_insnhelper.c:1754
#21 0x00007f032a0b8385 in vm_exec_core (th=th@entry=0x1ed95b0, initial=initial@entry=0) at insns.def:999
#22 0x00007f032a0bb5ec in vm_exec (th=0x1ed95b0) at vm.c:1304
#23 0x00007f032a0c43c9 in rb_iseq_eval (iseqval=<optimized out>) at vm.c:1549
#24 0x00007f0329f6a630 in rb_load_internal0 (th=0x1ed95b0, fname=52100160, wrap=wrap@entry=0) at load.c:615
#25 0x00007f0329f6bdde in rb_load_internal (wrap=0, fname=<optimized out>) at load.c:644
#26 rb_require_safe (fname=52099680, safe=0) at load.c:996
#27 0x00007f032a0bfae1 in vm_call_cfunc_with_frame (ci=<optimized out>, reg_cfp=0x7f032a5c0f70, th=0x1ed95b0) at vm_insnhelper.c:1470
#28 vm_call_cfunc (ci=<optimized out>, reg_cfp=0x7f032a5c0f70, th=0x1ed95b0) at vm_insnhelper.c:1560
#29 vm_call_method (th=0x1ed95b0, cfp=0x7f032a5c0f70, ci=<optimized out>) at vm_insnhelper.c:1754
#30 0x00007f032a0b7a44 in vm_exec_core (th=th@entry=0x1ed95b0, initial=initial@entry=0) at insns.def:1028
#31 0x00007f032a0bb5ec in vm_exec (th=th@entry=0x1ed95b0) at vm.c:1304
#32 0x00007f032a0c4636 in rb_iseq_eval_main (iseqval=iseqval@entry=52095080) at vm.c:1562
#33 0x00007f0329f6510a in ruby_exec_internal (n=0x31ae868) at eval.c:253
#34 0x00007f0329f670ad in ruby_exec_node (n=n@entry=0x31ae868) at eval.c:318
#35 0x00007f0329f694dc in ruby_run_node (n=0x31ae868) at eval.c:310
#36 0x000000000040088b in main (argc=3, argv=0x7fff3bba2b88) at main.c:36
```

I then thought I might get a bit more info if I dumped the current Ruby backtrace:

```
(gdb) call (void) close(1)
(gdb) call (void) close(2)
(gdb) shell tty
/dev/pts/15 <--- this will likely be different on your machine
(gdb) call (int) open("/dev/pts/15", 2, 0)
$1 = 1
(gdb) call (int) open("/dev/pts/15", 2, 0)
$2 = 2
(gdb) call (void)rb_backtrace()
```

This now shows me what's going on inside my Ruby process:

```
  gems/ruby-2.1.1/gems/puma-2.8.2/lib/puma/thread_pool.rb:92:in `block in spawn_thread'
  gems/ruby-2.1.1/gems/puma-2.8.2/lib/puma/thread_pool.rb:92:in `call'
  gems/ruby-2.1.1/gems/puma-2.8.2/lib/puma/server.rb:254:in `block in run'
  gems/ruby-2.1.1/gems/puma-2.8.2/lib/puma/server.rb:361:in `process_client'
  gems/ruby-2.1.1/gems/puma-2.8.2/lib/puma/server.rb:490:in `handle_request'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/content_length.rb:14:in `call'
  gems/ruby-2.1.1/gems/railties-4.1.1/lib/rails/application.rb:144:in `call'
  gems/ruby-2.1.1/gems/railties-4.1.1/lib/rails/engine.rb:514:in `call'
  gems/ruby-2.1.1/gems/airbrake-4.0.0/lib/airbrake/user_informer.rb:12:in `call'
  gems/ruby-2.1.1/gems/airbrake-4.0.0/lib/airbrake/user_informer.rb:16:in `_call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/sendfile.rb:112:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/static.rb:64:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/lock.rb:17:in `call'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/cache/strategy/local_cache_middleware.rb:26:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/runtime.rb:17:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/methodoverride.rb:21:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/request_id.rb:21:in `call'
  gems/ruby-2.1.1/gems/quiet_assets-1.0.2/lib/quiet_assets.rb:18:in `call_with_quiet_assets'
  gems/ruby-2.1.1/gems/railties-4.1.1/lib/rails/rack/logger.rb:20:in `call'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/tagged_logging.rb:68:in `tagged'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/tagged_logging.rb:26:in `tagged'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/tagged_logging.rb:68:in `block in tagged'
  gems/ruby-2.1.1/gems/railties-4.1.1/lib/rails/rack/logger.rb:20:in `block in call'
  gems/ruby-2.1.1/gems/railties-4.1.1/lib/rails/rack/logger.rb:38:in `call_app'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/show_exceptions.rb:30:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/debug_exceptions.rb:17:in `call'
  gems/ruby-2.1.1/gems/airbrake-4.0.0/lib/airbrake/rails/middleware.rb:13:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/remote_ip.rb:76:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/reloader.rb:73:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/callbacks.rb:27:in `call'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:82:in `run_callbacks'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/callbacks.rb:29:in `block in call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/cookies.rb:560:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/session/abstract/id.rb:220:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/session/abstract/id.rb:225:in `context'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/flash.rb:254:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/middleware/params_parser.rb:27:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/head.rb:11:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/conditionalget.rb:25:in `call'
  gems/ruby-2.1.1/gems/rack-1.5.2/lib/rack/etag.rb:23:in `call'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/manager.rb:34:in `call'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/manager.rb:34:in `catch'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/manager.rb:35:in `block in call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/routing/route_set.rb:676:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/journey/router.rb:59:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/journey/router.rb:59:in `each'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/journey/router.rb:71:in `block in call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/routing/route_set.rb:48:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/routing/route_set.rb:80:in `dispatch'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_dispatch/routing/route_set.rb:80:in `call'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal.rb:231:in `block in action'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal/rack_delegation.rb:13:in `dispatch'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal.rb:195:in `dispatch'
  gems/ruby-2.1.1/gems/actionview-4.1.1/lib/action_view/rendering.rb:30:in `process'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/abstract_controller/base.rb:136:in `process'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal/params_wrapper.rb:250:in `process_action'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal/instrumentation.rb:30:in `process_action'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/notifications.rb:159:in `instrument'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/notifications/instrumenter.rb:20:in `instrument'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/notifications.rb:159:in `block in instrument'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal/instrumentation.rb:31:in `block in process_action'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/action_controller/metal/rescue.rb:29:in `process_action'
  gems/ruby-2.1.1/gems/actionpack-4.1.1/lib/abstract_controller/callbacks.rb:19:in `process_action'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:86:in `run_callbacks'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:86:in `call'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:166:in `block in halting'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:166:in `call'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:160:in `block in halting'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:160:in `call'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:440:in `block in make_lambda'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/callbacks.rb:440:in `instance_exec'
  gems/ruby-2.1.1/gems/mongoid_userstamp-0.3.2/lib/mongoid/userstamp/railtie.rb:15:in `block (2 levels) in <class:Railtie>'
  gems/ruby-2.1.1/gems/devise-3.2.4/lib/devise/controllers/helpers.rb:58:in `current_user'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/proxy.rb:104:in `authenticate'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/proxy.rb:318:in `_perform_authentication'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/proxy.rb:212:in `user'
  gems/ruby-2.1.1/gems/warden-1.2.3/lib/warden/session_serializer.rb:34:in `fetch'
  gems/ruby-2.1.1/gems/devise-3.2.4/lib/devise.rb:462:in `block (2 levels) in configure_warden!'
  gems/ruby-2.1.1/gems/devise-3.2.4/lib/devise/models/authenticatable.rb:208:in `serialize_from_session'
  gems/ruby-2.1.1/gems/orm_adapter-0.5.0/lib/orm_adapter/adapters/mongoid.rb:22:in `get'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/contextual.rb:20:in `first'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/contextual/mongo.rb:197:in `first'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/contextual/mongo.rb:447:in `try_cache'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/contextual/mongo.rb:198:in `block in first'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/contextual/mongo.rb:535:in `with_sorting'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/contextual/mongo.rb:199:in `block (2 levels) in first'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/query_cache.rb:186:in `first_with_cache'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/query_cache.rb:135:in `with_cache'
  gems/ruby-2.1.1/bundler/gems/mongoid-49bc68fd3011/lib/mongoid/query_cache.rb:187:in `block in first_with_cache'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/query.rb:127:in `first'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/read_preference/primary.rb:54:in `with_node'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/read_preference/selectable.rb:65:in `with_retry'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/read_preference/selectable.rb:65:in `call'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/read_preference/primary.rb:55:in `block in with_node'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/cluster.rb:240:in `with_primary'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/cluster.rb:151:in `nodes'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/cluster.rb:194:in `refresh'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/cluster.rb:194:in `each'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/cluster.rb:182:in `block in refresh'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:432:in `refresh'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:90:in `command'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:648:in `read'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/operation/read.rb:48:in `execute'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:391:in `process'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:587:in `flush'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:616:in `logging'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/instrumentable.rb:31:in `instrument'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/notifications.rb:159:in `instrument'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/notifications/instrumenter.rb:20:in `instrument'
  gems/ruby-2.1.1/gems/activesupport-4.1.1/lib/active_support/notifications.rb:159:in `block in instrument'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:617:in `block in logging'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:589:in `block in flush'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:187:in `ensure_connected'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:184:in `rescue in ensure_connected'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/failover/retry.rb:29:in `execute'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:114:in `connection'
  gems/ruby-2.1.1/gems/connection_pool-2.0.0/lib/connection_pool.rb:58:in `with'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:115:in `block in connection'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/failover/retry.rb:30:in `block in execute'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/node.rb:590:in `block (2 levels) in flush'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection.rb:172:in `write'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection.rb:220:in `with_connection'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection.rb:52:in `connect'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/connectable.rb:144:in `connect'
  rubies/ruby-2.1.1/lib/ruby/2.1.0/timeout.rb:106:in `timeout'
  rubies/ruby-2.1.1/lib/ruby/2.1.0/timeout.rb:35:in `catch'
  rubies/ruby-2.1.1/lib/ruby/2.1.0/timeout.rb:35:in `catch'
  rubies/ruby-2.1.1/lib/ruby/2.1.0/timeout.rb:35:in `block in catch'
  rubies/ruby-2.1.1/lib/ruby/2.1.0/timeout.rb:91:in `block in timeout'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/connectable.rb:145:in `block in connect'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/connectable.rb:145:in `new'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/tcp.rb:20:in `initialize'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/connectable.rb:119:in `handle_socket_errors'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/tcp.rb:20:in `block in initialize'
  gems/ruby-2.1.1/bundler/gems/moped-074ba070aa98/lib/moped/connection/socket/tcp.rb:20:in `initialize'
```

Looks like the whole think started with a [moped](https://github.com/mongoid/moped) socket connection (which makes sense).

Investigating further ...