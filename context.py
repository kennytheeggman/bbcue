from ui.component import Component, create_component_context

c = create_component_context()
c2 = create_component_context()


# print(dir(c))

def ccontent(params, props):

    return f"{params['test']} {props['test']}"
test = c.component({'test': 1203978})(ccontent)
# print(test)

newc = test({'test': 239080})

print(newc)

@c.class_file(c, "/slider")
def sli(props):

    return f"{props['test']}"

# print(c._cparams)
print(Component.files)
# print(c._cparams)
# print(c.files)