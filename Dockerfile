FROM debian
EXPOSE 8888
RUN apt-get update && apt-get install -y python3
ADD ./futon_dynamics.par /futon-dynamics
CMD /futon-dynamics
