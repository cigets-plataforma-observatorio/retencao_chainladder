import chainladder as cl
from tratamentos import gerar_triangulo


def treinar_chainladder(cohort_pivot):
    triangulo = gerar_triangulo(cohort_pivot)

    cl_triangle = cl.Triangle(
        triangulo,
        origin="origin",
        development="development",
        columns="values",
        cumulative=True
    )

    cl_pipeline = cl.Pipeline([("dev", cl.Development()), ("tail", cl.TailCurve())]).fit_transform(cl_triangle)
    cl_model = cl.Chainladder().fit(cl_pipeline)

    return cl_model
