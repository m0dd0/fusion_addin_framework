# Design decisions
## dynamic command.doExecute() realization
The core problem is that we wnat to execute the commands execute handler from a thread with an arbitrary function.
However the Fusion command class instance can only be accessed from the event handler and therfore we need to save this command object somewhere (globally) to ensure that we can access the command.doExecute() method from the thread.
Additionaly we need to have an execution_queue where we store the action which should be executed after calling command.doExecute().
Also this execution queue must be accessible from the thread and the executeevent handler.
The native (without framework approach) is to have a global variable fusion_command which is set from the commandCreated event and also a global execution_queue.
In larger projects this solution becomes more and more ugly as we often face circular imports on the global objects etc.
Therefore globally accesible utility in the framework lets us simply execute a Callable from the currently active command would be nice to have.
Alternative framework-wise approaches would be a realization in the addin or command instances.
However that would again have the downside that we need to store a global addin or command instance to be accessed from out thread function.
A possible solution would be to implement a additional executeHandler_ which always checks a framework-global execution_queue before it executes its "real" behavior.
This approach gets tricky since we need to differentiate between a execute-call from a thread ot a normal call as we normally dont want the normal action to be executed when we call it from a thread.
In the end it seems to be beter to keep the command.doExecute() management at the application level and NOT integrate it into the framework.
Possible patterns for realiting it can be seen in the CADTris addin. 
A first attempt fot the framework wise solution is in the dynamic_do_Execute branch.