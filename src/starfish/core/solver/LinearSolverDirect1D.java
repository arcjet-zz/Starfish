/*
 * (c) 2012-2018 Particle In Cell Consulting LLC
 * 
 * Implements a 1D solver in which data along the minor dimension is averaged
 * this should be general to support either dimension but for now hardoded for "i" since
 * no clear way how to pass this information to the solver
 *
 * This document is subject to the license specified in 
 * Starfish.java and the LICENSE file
 */
package starfish.core.solver;

import starfish.core.common.Constants;
import starfish.core.common.Starfish;
import starfish.core.common.Starfish.Log;
import starfish.core.domain.FieldCollection2D;
import starfish.core.domain.Mesh;
import starfish.core.solver.Solver.LinearSolver;
import starfish.core.solver.Solver.MeshData;

/**
 *
 * @author Lubos Brieda
 */
public class LinearSolverDirect1D implements LinearSolver
{
    
    @Override
    public int solve(Solver.MeshData[] mesh_data, FieldCollection2D fc, int max_it, double tolerance)
    {
	/*supports only mesh*/
	if (mesh_data.length>1 && Starfish.getIt()==0)
	    Log.warning("LinearSolverDirect1D not yet implemented for multiple domains");
	
	MeshData md = mesh_data[0];
	Mesh mesh = md.mesh;
	
	double a[] = new double[mesh.ni];
	double b[] = new double[mesh.ni];
	double c[] = new double[mesh.ni];
	double d[] = new double[mesh.ni];
	double w[] = new double[mesh.ni];
	double x[] = new double[mesh.ni];
	
	for (int i=0;i<mesh.ni;i++)
	{
	    d[i] = 0;
	    /*average RHS data*/
	    for (int j=0;j<mesh.nj;j++)
	    {
		int u = mesh.IJtoN(i, j);
		d[i] += md.b[u];		
	    }
	    d[i] /= mesh.nj;
	}
	
	/*apply filtering*/
	boolean filtering = true;
	if (filtering)
	{
	    double alpha = 0.7;	//large value to keep tight corners
	    int nn = d.length;
	    
	    for (int s=0;s<10;s++)  //repeat smoothing 10 times
	    {	    
		//forward
		double df[] = new double[nn];
		df[1] = d[1];   //skip first node as b.c.
		for (int i=2;i<nn-1;i++)
		    df[i] = (1-alpha)*df[i-1] + alpha*d[i];

		//backward
		double db[] = new double[nn];
		db[nn-2] = d[nn-2];
		for (int i=nn-2;i>=1;i--)
		    db[i] = (1-alpha)*db[i+1]+alpha*d[i];

		for (int i=1;i<nn-1;i++) //skip boundaries
		{
		    int nj_half = (int)(0.5*mesh.nj);
		    if (!mesh.isDirichletNode(i,nj_half))
			d[i] = 0.5*(df[i]+db[i]);	//average
		}
	    }
	    
	    /*set global data*/
	    double rho[][] = Starfish.domain_module.getRho(mesh).getData();
	    for (int i=0;i<mesh.ni;i++)
		for (int j=0;j<mesh.nj;j++)
		    if (!mesh.isDirichletNode(i,j))
			rho[i][j] = d[i]*Constants.EPS0;
	    
	}
	
	/*initialize coefficients to those along midpoint*/
	int nj_half = (int)(0.5*mesh.nj);
	double dx = mesh.pos1(1,0) - mesh.pos1(0,0);
	for (int i=1;i<mesh.ni-1;i++)
	{
	   if (mesh.isDirichletNode(i,nj_half))
	   {
	       a[i] = 0;
	       b[i] = 1;
	       c[i] = 0;
	   }
	   else
	   {
		a[i] = 1/(dx*dx);
		b[i] = -2/(dx*dx);
		c[i] = 1/(dx*dx);
	   }
	}
	
	/*boundaries*/
	if (mesh.isDirichletNode(0,nj_half))
	{
	    a[0] = 0;
	    b[0] = 1;
	    c[0] = 0;
	}
	else
	{
	    a[0] = 0;
	    b[0] = 1;
	    c[0] = -1;
	}
	
	if (mesh.isDirichletNode(mesh.ni-1,nj_half))
	{
	    a[mesh.ni-1] = 0;
	    b[mesh.ni-1] = 1;
	    c[mesh.ni-1] = 1;
	}
	else
	{
	    a[mesh.ni-1] = -1;
	    b[mesh.ni-1] = 1;
	    c[mesh.ni-1] = 0;
	}
	 
	/*forward sweep, non-coefficient preserving method from wikipedia*/
	for (int i=1;i<mesh.ni;i++)
	{
	    w[i] = a[i]/b[i-1];
	    b[i] -= w[i]*c[i-1];
	    d[i] -= w[i]*d[i-1];
	}
	
	/*back substitution*/
	x[mesh.ni-1] = d[mesh.ni-1]/b[mesh.ni-1];
	for (int i=mesh.ni-2;i>=0;i--)
	    x[i] = (d[i]-c[i]*x[i+1])/b[i];
	
	/*now populate the 1D solution to the 2D array*/
	for (int i=0;i<mesh.ni;i++)
	    for (int j=0;j<mesh.nj;j++)
	    {
		int u = mesh.IJtoN(i,j);
		md.x[u] = x[i];
	    }
	return 0;
    }
    
}
