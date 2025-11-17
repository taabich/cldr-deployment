oc new-project cldr 
oc project cldr<NAMESPACE>
oc apply -f ocp-cldr-ansible.yaml
oc start-build cldr-ansible --from-dir=. --follow -n cldr
oc rollout status dc/cldr-ansible -n cldr
POD=$(oc get pod -l app=cldr-ansible -n cldr -o name | head -1)

#oc rsh -n cldr "${POD#pod/}"