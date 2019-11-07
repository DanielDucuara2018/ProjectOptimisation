package solver;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.xml.stream.FactoryConfigurationError;
import javax.xml.stream.XMLStreamException;

import params.Params;
import problem.Acquisition;
import problem.CandidateAcquisition;
import problem.DownloadWindow;
import problem.PlanningProblem;
import problem.RecordedAcquisition;
import problem.ProblemParserXML;
import problem.Satellite;

/**
 * Class implementing a download planner which tries to insert downloads into
 * the plan by ordering acquisitions following an increasing order of their
 * realization time, and by considering download windows chronologically
 * 
 * @author cpralet
 *
 */
public class BadDownloadPlanner {

	public static void planDownloads(SolutionPlan plan, String solutionFilename) throws IOException {

		PlanningProblem pb = plan.pb;
		List<CandidateAcquisition> acqPlan = plan.plannedAcquisitions;

		PrintWriter writer = new PrintWriter(new BufferedWriter(new FileWriter(solutionFilename, false)));

		boolean firstLine = true;
		double totalTimeOnBoard = 0;
		int totalNumberAcquisitionDownloaded = 0;

		int totalCandidates = 0;
		
		// plan downloads for each satellite independently (solution which might violate
		// some constraints for large constellations)
		for (Satellite satellite : pb.satellites) {
			// get all recorded acquisitions associated with this satellite
			List<Acquisition> candidateDownloads = new ArrayList<Acquisition>();
			for (RecordedAcquisition dl : pb.recordedAcquisitions) {
				if (dl.satellite == satellite)
					// System.out.println(dl.getAcquisitionTime());
					candidateDownloads.add(dl);
			}
			// get all planned acquisitions associated with this satellite
			for (CandidateAcquisition a : acqPlan) {
				if (a.selectedAcquisitionWindow.satellite == satellite)
					candidateDownloads.add(a);
			}			
			 
			// Determinate priority and non priority acquisitions
			List<Acquisition> nonPrioCandidateDownloads = new ArrayList<Acquisition>();
			List<Acquisition> prioCandidateDownloads = new ArrayList<Acquisition>();
			for (Acquisition cd : candidateDownloads) {
				if(cd.getPriority() == 0) prioCandidateDownloads.add(cd);
				else nonPrioCandidateDownloads.add(cd);	
			}
			
			//sort priority acquisitions by increasing start time
			prioCandidateDownloads = sortFunction(prioCandidateDownloads);
			//sort non priority acquisitions by increasing start time
			nonPrioCandidateDownloads = sortFunction(nonPrioCandidateDownloads);
			
			//contenate priority and non priority acquisition list
			candidateDownloads = new ArrayList<Acquisition>(prioCandidateDownloads);
			candidateDownloads.addAll(nonPrioCandidateDownloads);
			
			for (Acquisition cd : candidateDownloads) {
				System.out.println(cd.getPriority() + " " + cd.getAcquisitionTime());
			}
			
			// sort download windows by increasing start time
			List<DownloadWindow> downloadWindows = new ArrayList<DownloadWindow>();
			for (DownloadWindow w : pb.downloadWindows) {
				if (w.satellite == satellite)
					downloadWindows.add(w);
			}
			Collections.sort(downloadWindows, new Comparator<DownloadWindow>() {
				@Override
				public int compare(DownloadWindow a0, DownloadWindow a1) {
					double start0 = a0.start;
					double start1 = a1.start;
					if (start0 < start1)
						return -1;
					if (start0 > start1)
						return 1;
					return 0;
				}
			});
			if (downloadWindows.isEmpty())
				continue;
			
			totalCandidates += candidateDownloads.size();
			
			Map<Double, Acquisition> candidateDl;			
			double lastTimeDownloadWindow = 0;
			for (DownloadWindow w : downloadWindows) {
				double startTime = Math.max(w.start, lastTimeDownloadWindow);
				double endTime = w.end;
				double max = 0;
				do {
					candidateDl = new HashMap<Double, Acquisition>();
					for (Acquisition a : candidateDownloads) {
						double dlDuration = a.getVolume() / Params.downlinkRate;
						double timeOnBoard = startTime - a.getAcquisitionTime();
						if (a.getAcquisitionTime() < startTime && (dlDuration + startTime) < endTime) {
							candidateDl.put(timeOnBoard, a);
						}
					}
					if (!candidateDl.isEmpty()) {
						max = Collections.max(candidateDl.keySet());
						Acquisition a = candidateDl.get(max);
						

						double dlDuration = a.getVolume() / Params.downlinkRate;

						if (firstLine) {
							firstLine = false;
						} else
							writer.write("\n");
						
						totalTimeOnBoard += startTime - a.getAcquisitionTime();
						totalNumberAcquisitionDownloaded++;
						
						if (a instanceof RecordedAcquisition)
							writer.write("REC " + ((RecordedAcquisition) a).idx + " " + w.idx + " " + startTime + " "
									+ (startTime + dlDuration));
						else // case CandidateAcquisition
							writer.write("CAND " + ((CandidateAcquisition) a).idx + " " + w.idx + " " + startTime + " "
									+ (startTime + dlDuration));

						startTime += dlDuration;
						candidateDownloads.remove(a);					
					}

				} while (!candidateDl.isEmpty());
				lastTimeDownloadWindow = startTime;
			}
			System.out.println("candidate sin vaciar " + candidateDownloads.size());
			
		}
		
		System.out.println("Average time on board " + totalTimeOnBoard / totalNumberAcquisitionDownloaded + " Acquisition Downloaded " + totalNumberAcquisitionDownloaded);
		System.out.println("candidate inicial " + totalCandidates);
		writer.flush();
		writer.close();
	}
	
	public static List<Acquisition> sortFunction(List<Acquisition> a) {
		// sort acquisitions by increasing start time
		Collections.sort(a, new Comparator<Acquisition>() {
			@Override
			public int compare(Acquisition a0, Acquisition a1) {
				double start0 = a0.getAcquisitionTime();
				double start1 = a1.getAcquisitionTime();
				if (start0 < start1)
					return -1;
				if (start0 > start1)
					return 1;
				return 0;
			}

		});
		return a;
	}

	public static void main(String[] args)
			throws XMLStreamException, FactoryConfigurationError, IOException, ParseException {
		ProblemParserXML parser = new ProblemParserXML();
		PlanningProblem pb = parser.read(Params.systemDataFile, Params.planningDataFile);
		SolutionPlan plan = new SolutionPlan(pb);
		int nSatellites = pb.satellites.size();
		for (int i = 1; i <= nSatellites; i++)
			plan.readAcquisitionPlan("output/solutionAcqPlan_SAT" + i + ".txt");
		planDownloads(plan, "output/downloadPlan.txt");
	}

}
